package agent

import (
	"context"
	"reflect"
	"testing"
)

func TestRunnerPublishesEachFinishedStepBeforeTheNext(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		chunkedGenerator([]string{
			`<tool_call>{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
			`<tool_call>{"name":"echo","arguments":{"value":"pong"}}</tool_call>`,
			"Echo 返回了 ping 和 pong。",
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 4, Protocol: G1Protocol{}, Renderer: RWKVChatRenderer{}},
	)
	if err != nil {
		t.Fatal(err)
	}
	var events []Event
	result, err := runner.RunWithObserver(context.Background(), "Check the echo tool twice", func(event Event) {
		events = append(events, event)
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(result.Steps) != 3 {
		t.Fatalf("steps = %d, want 3", len(result.Steps))
	}
	var published []Step
	for index, event := range events {
		if event.Kind != EventStepDone {
			continue
		}
		if event.StepTrace == nil || event.Step != event.StepTrace.Number {
			t.Fatalf("step_done without a matching trace: %+v", event)
		}
		// The step is published right before the next one starts.
		if next := events[index+1]; next.Kind != EventModelStart || next.Step != event.Step+1 {
			t.Fatalf("step_done %d followed by %+v", event.Step, next)
		}
		published = append(published, *event.StepTrace)
	}
	// Every step but the last arrives live, already identical to the settled trace.
	if !reflect.DeepEqual(published, result.Steps[:2]) {
		t.Fatalf("published steps differ from the result:\n%+v\n%+v", published, result.Steps[:2])
	}
	if published[0].ToolResult == nil || published[0].Tool != "echo" {
		t.Fatalf("published step lacks its tool result: %+v", published[0])
	}
}
