package concurrent

import (
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/inference"
)

type SessionPhase string

const (
	PhaseQueued     SessionPhase = "queued"
	PhasePrefill    SessionPhase = "prefill"
	PhaseGenerating SessionPhase = "generating"
	PhaseDone       SessionPhase = "done"
	PhaseCancelled  SessionPhase = "cancelled"
	PhaseError      SessionPhase = "error"
)

type RunPhase string

const (
	RunPreparing  RunPhase = "preparing"
	RunRunning    RunPhase = "running"
	RunFollowing  RunPhase = "following-up"
	RunCancelling RunPhase = "cancelling"
	RunCompleted  RunPhase = "completed"
	RunCancelled  RunPhase = "cancelled"
	RunFailed     RunPhase = "failed"
)

type SessionSnapshot struct {
	Index        int
	Phase        SessionPhase
	Output       string
	PromptTokens int
	OutputTokens int
	PrefillDone  int
	PrefillTotal int
	DecodeTPS    float64
	Elapsed      time.Duration
	FinishReason inference.FinishReason
	Err          error
}

type RunSnapshot struct {
	Phase          RunPhase
	Sessions       []SessionSnapshot
	StartedAt      time.Time
	Elapsed        time.Duration
	MaxNativeBatch int
	TotalTokens    int
	AggregateTPS   float64
	Done           bool
}

type Summary struct {
	Sessions       int
	MaxNativeBatch int
	Tokens         int
	Elapsed        time.Duration
	AggregateTPS   float64
	Cancelled      bool
}

func (s Summary) String() string {
	status := "complete"
	if s.Cancelled {
		status = "cancelled"
	}
	return fmt.Sprintf(
		"Concurrent batch %s: sessions=%d max_native_batch=%d tokens=%d elapsed=%s aggregate=%.1f tok/s",
		status,
		s.Sessions,
		s.MaxNativeBatch,
		s.Tokens,
		s.Elapsed.Round(time.Millisecond),
		s.AggregateTPS,
	)
}

func cloneSnapshot(source RunSnapshot) RunSnapshot {
	result := source
	result.Sessions = append([]SessionSnapshot(nil), source.Sessions...)
	return result
}

func sessionErrors(sessions []SessionSnapshot) error {
	var messages []string
	for _, session := range sessions {
		if session.Err != nil && session.Phase != PhaseCancelled {
			messages = append(messages, fmt.Sprintf("session %d: %v", session.Index, session.Err))
		}
	}
	if len(messages) == 0 {
		return nil
	}
	return fmt.Errorf("%s", strings.Join(messages, "; "))
}
