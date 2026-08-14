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
	Output    string               `json:"output"`
	Sources   []string             `json:"sources,omitempty"`
	Route     agent.Route          `json:"route,omitempty"`
	Bundles   []string             `json:"bundles,omitempty"`
	Steps     []agent.SubagentStep `json:"steps,omitempty"`
	StepCount int                  `json:"step_count,omitempty"`
}

type AgentTaskRunner func(context.Context, string, func(agent.Event)) (AgentTaskResult, error)

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

type SpawnAgentsResult struct {
	Results []agent.SubagentTrace `json:"results"`
}

func (r SpawnAgentsResult) SubagentTraces() []agent.SubagentTrace {
	return r.Results
}

// MarshalJSON preserves the tool payload the parent model already sees. The
// richer route and step trace travels separately through SubagentTraces.
func (r SpawnAgentsResult) MarshalJSON() ([]byte, error) {
	type delegatedResult struct {
		Index      int      `json:"index"`
		Task       string   `json:"task"`
		Output     string   `json:"output,omitempty"`
		Sources    []string `json:"sources,omitempty"`
		Steps      int      `json:"steps,omitempty"`
		DurationMS int64    `json:"duration_ms"`
		Error      string   `json:"error,omitempty"`
	}
	results := make([]delegatedResult, 0, len(r.Results))
	for _, value := range r.Results {
		stepCount := value.StepCount
		if stepCount == 0 {
			stepCount = len(value.Steps)
		}
		results = append(results, delegatedResult{
			Index: value.Index, Task: value.Task, Output: value.Output,
			Sources: append([]string(nil), value.Sources...), Steps: stepCount,
			DurationMS: value.DurationMS, Error: value.Error,
		})
	}
	return json.Marshal(struct {
		Results []delegatedResult `json:"results"`
	}{Results: results})
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
	results := make([]agent.SubagentTrace, len(tasks))
	var wait sync.WaitGroup
	var eventMu sync.Mutex
	emit := func(event agent.Event) {
		eventMu.Lock()
		defer eventMu.Unlock()
		agent.EmitToolEvent(ctx, event)
	}
	wait.Add(len(tasks))
	for index, task := range tasks {
		go func() {
			defer wait.Done()
			started := time.Now()
			emit(agent.Event{
				Kind: agent.EventSubagentStart, SubagentIndex: index + 1, SubagentTask: task,
			})
			result, err := t.options.Run(batchContext, task, func(event agent.Event) {
				event.SubagentIndex = index + 1
				event.SubagentTask = task
				emit(event)
			})
			item := agent.SubagentTrace{
				Index:      index + 1,
				Task:       task,
				Status:     "completed",
				Output:     strings.TrimSpace(result.Output),
				Sources:    append([]string(nil), result.Sources...),
				Route:      result.Route,
				Bundles:    append([]string(nil), result.Bundles...),
				Steps:      append([]agent.SubagentStep(nil), result.Steps...),
				StepCount:  result.StepCount,
				DurationMS: time.Since(started).Milliseconds(),
			}
			if err != nil {
				item.Error = err.Error()
				item.Status = "failed"
			}
			results[index] = item
			emit(agent.Event{
				Kind: agent.EventSubagentDone, SubagentIndex: index + 1, SubagentTask: task,
				Route: result.Route, Bundles: append([]string(nil), result.Bundles...),
				DurationMS: item.DurationMS, Err: err,
			})
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
				results[index].Status = "failed"
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
		return SpawnAgentsResult{Results: results}, fmt.Errorf("all %d delegated tasks failed", failed)
	}
	return SpawnAgentsResult{Results: results}, nil
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
