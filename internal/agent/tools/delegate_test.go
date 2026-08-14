package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"sync/atomic"
	"testing"
	"time"
)

func TestSpawnAgentsRunsTasksConcurrentlyAndPreservesOrder(t *testing.T) {
	t.Parallel()
	var active atomic.Int32
	var maximum atomic.Int32
	tool := DelegationTools(DelegationOptions{
		MaxParallel: 4,
		Timeout:     time.Second,
		Run: func(_ context.Context, task string) (AgentTaskResult, error) {
			current := active.Add(1)
			defer active.Add(-1)
			for current > maximum.Load() && !maximum.CompareAndSwap(maximum.Load(), current) {
			}
			time.Sleep(20 * time.Millisecond)
			return AgentTaskResult{Output: "done:" + task, Steps: 2}, nil
		},
	})[0]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"tasks":["official","independent","contradictions"],"max_depth":1}`))
	if err != nil {
		t.Fatal(err)
	}
	if maximum.Load() < 2 {
		t.Fatalf("maximum concurrency = %d", maximum.Load())
	}
	encoded, _ := json.Marshal(value)
	text := string(encoded)
	for index, task := range []string{"official", "independent", "contradictions"} {
		expected := fmt.Sprintf(`"index":%d,"task":"%s","output":"done:%s"`, index+1, task, task)
		if !containsJSONFields(text, expected) {
			t.Fatalf("result %s does not contain %s", text, expected)
		}
	}
}

func TestSpawnAgentsRejectsSingleTask(t *testing.T) {
	t.Parallel()
	tool := DelegationTools(DelegationOptions{Run: func(context.Context, string) (AgentTaskResult, error) {
		return AgentTaskResult{}, nil
	}})[0]
	if _, err := tool.Execute(context.Background(), json.RawMessage(`{"tasks":["only"]}`)); err == nil {
		t.Fatal("spawn_agents accepted one task")
	}
}

func TestSpawnAgentsAcceptsObjectTaskAliases(t *testing.T) {
	t.Parallel()
	tool := DelegationTools(DelegationOptions{Run: func(_ context.Context, task string) (AgentTaskResult, error) {
		return AgentTaskResult{Output: "done:" + task}, nil
	}})[0]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"tasks":[{"task":"official"},{"description":"independent","tools":["calculator"]}]}`))
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(value)
	if text := string(encoded); !containsJSONFields(text, `"task":"official","output":"done:official"`) ||
		!containsJSONFields(text, `"task":"independent","output":"done:independent"`) {
		t.Fatalf("result = %s", text)
	}
}

func TestSpawnAgentsReturnsErrorWhenEveryTaskFails(t *testing.T) {
	t.Parallel()
	tool := DelegationTools(DelegationOptions{Run: func(_ context.Context, task string) (AgentTaskResult, error) {
		return AgentTaskResult{}, fmt.Errorf("%s failed", task)
	}})[0]
	if _, err := tool.Execute(context.Background(), json.RawMessage(`{"tasks":["official","independent"]}`)); err == nil || err.Error() != "all 2 delegated tasks failed" {
		t.Fatalf("error = %v", err)
	}
}

func TestSpawnAgentsKeepsPartialResults(t *testing.T) {
	t.Parallel()
	tool := DelegationTools(DelegationOptions{Run: func(_ context.Context, task string) (AgentTaskResult, error) {
		if task == "failed" {
			return AgentTaskResult{}, fmt.Errorf("unavailable")
		}
		return AgentTaskResult{Output: "done:" + task}, nil
	}})[0]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"tasks":["successful","failed"]}`))
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(value)
	if text := string(encoded); !containsJSONFields(text, `"task":"successful","output":"done:successful"`) || !containsJSONFields(text, `"task":"failed"`) || !containsJSONFields(text, `"error":"unavailable"`) {
		t.Fatalf("result = %s", text)
	}
}

func TestSpawnAgentsPreservesParentCancellation(t *testing.T) {
	t.Parallel()
	contextValue, cancel := context.WithCancel(context.Background())
	tool := DelegationTools(DelegationOptions{Run: func(ctx context.Context, _ string) (AgentTaskResult, error) {
		<-ctx.Done()
		return AgentTaskResult{}, ctx.Err()
	}})[0]
	cancel()
	if _, err := tool.Execute(contextValue, json.RawMessage(`{"tasks":["one","two"]}`)); err != context.Canceled {
		t.Fatalf("error = %v", err)
	}
}

func containsJSONFields(text string, fields string) bool {
	return len(text) >= len(fields) && findSubstring(text, fields) >= 0
}

func findSubstring(text string, target string) int {
	for index := 0; index+len(target) <= len(text); index++ {
		if text[index:index+len(target)] == target {
			return index
		}
	}
	return -1
}
