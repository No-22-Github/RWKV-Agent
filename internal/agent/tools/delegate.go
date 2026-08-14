package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

type AgentTaskResult struct {
	Output  string   `json:"output"`
	Sources []string `json:"sources,omitempty"`
	Steps   int      `json:"steps,omitempty"`
}

type AgentTaskRunner func(context.Context, string) (AgentTaskResult, error)

type DelegationOptions struct {
	Run         AgentTaskRunner
	MaxParallel int
	Timeout     time.Duration
}

func DelegationTools(options DelegationOptions) []agent.Tool {
	if options.MaxParallel <= 0 {
		options.MaxParallel = 4
	}
	if options.MaxParallel > 8 {
		options.MaxParallel = 8
	}
	if options.Timeout <= 0 {
		options.Timeout = 2 * time.Minute
	}
	return []agent.Tool{&spawnAgentsTool{options: options}}
}

type spawnAgentsTool struct{ options DelegationOptions }

func (t *spawnAgentsTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "spawn_agents",
		Description: fmt.Sprintf("Run 2 to %d independent Agent subtasks concurrently and return ordered results.", t.options.MaxParallel),
		Arguments:   `{"tasks":["independent subtask", "independent subtask"]}`,
		Parameters: json.RawMessage(fmt.Sprintf(
			`{"type":"object","properties":{"tasks":{"type":"array","items":{"type":"string","minLength":1,"maxLength":2000},"minItems":2,"maxItems":%d}},"required":["tasks"],"additionalProperties":false}`,
			t.options.MaxParallel,
		)),
		Strict:     true,
		Bundle:     agent.ToolBundleDelegate,
		Permission: agent.PermissionDelegate,
	}
}

type delegatedResult struct {
	Index      int      `json:"index"`
	Task       string   `json:"task"`
	Output     string   `json:"output,omitempty"`
	Sources    []string `json:"sources,omitempty"`
	Steps      int      `json:"steps,omitempty"`
	DurationMS int64    `json:"duration_ms"`
	Error      string   `json:"error,omitempty"`
}

func (t *spawnAgentsTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Tasks    json.RawMessage `json:"tasks"`
		MaxDepth json.RawMessage `json:"max_depth"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	tasks, err := normalizeDelegatedTasks(args.Tasks)
	if err != nil {
		return nil, err
	}
	if len(tasks) < 2 || len(tasks) > t.options.MaxParallel {
		return nil, invalidArguments("tasks must contain between 2 and %d entries", t.options.MaxParallel)
	}
	for index := range tasks {
		tasks[index] = strings.TrimSpace(tasks[index])
		if tasks[index] == "" {
			return nil, invalidArguments("tasks[%d] is empty", index)
		}
	}
	if t.options.Run == nil {
		return nil, agent.ErrProviderUnavailable
	}
	batchContext, cancel := context.WithTimeout(ctx, t.options.Timeout)
	defer cancel()
	results := make([]delegatedResult, len(tasks))
	var wait sync.WaitGroup
	wait.Add(len(tasks))
	for index, task := range tasks {
		go func() {
			defer wait.Done()
			started := time.Now()
			result, err := t.options.Run(batchContext, task)
			item := delegatedResult{
				Index:      index + 1,
				Task:       task,
				Output:     strings.TrimSpace(result.Output),
				Sources:    append([]string(nil), result.Sources...),
				Steps:      result.Steps,
				DurationMS: time.Since(started).Milliseconds(),
			}
			if err != nil {
				item.Error = err.Error()
			}
			results[index] = item
		}()
	}
	wait.Wait()
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if err := batchContext.Err(); err != nil && ctx.Err() == nil {
		for index := range results {
			if results[index].Output == "" && results[index].Error == "" {
				results[index].Error = err.Error()
			}
		}
	}
	failed := 0
	for _, result := range results {
		if result.Error != "" && result.Output == "" {
			failed++
		}
	}
	if failed == len(results) {
		return nil, fmt.Errorf("all %d delegated tasks failed", failed)
	}
	return map[string]any{"results": results}, nil
}

func normalizeDelegatedTasks(raw json.RawMessage) ([]string, error) {
	var tasks []string
	if json.Unmarshal(raw, &tasks) == nil {
		return tasks, nil
	}
	var objects []struct {
		Task        string `json:"task"`
		Prompt      string `json:"prompt"`
		Description string `json:"description"`
		Name        string `json:"name"`
	}
	if json.Unmarshal(raw, &objects) != nil {
		return nil, invalidArguments("tasks must be an array of strings or task objects")
	}
	tasks = make([]string, len(objects))
	for index, object := range objects {
		tasks[index] = object.Task
		if strings.TrimSpace(tasks[index]) == "" {
			tasks[index] = object.Prompt
		}
		if strings.TrimSpace(tasks[index]) == "" {
			tasks[index] = object.Description
		}
		if strings.TrimSpace(tasks[index]) == "" {
			tasks[index] = object.Name
		}
	}
	return tasks, nil
}
