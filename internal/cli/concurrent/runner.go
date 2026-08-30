package concurrent

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type Options struct {
	Conversation conversation.Options
	Turn         conversation.TurnOptions
	Prompt       string
	Concurrency  int
	BaseSeed     int64
}

type Runner struct {
	model inference.Model
	opts  Options

	operationMu   sync.Mutex
	mu            sync.RWMutex
	snapshot      RunSnapshot
	outputs       []strings.Builder
	conversations []*conversation.Conversation
	elapsedBase   time.Duration
	done          chan struct{}
	running       bool
	closed        bool
}

func NewRunner(model inference.Model, options Options) (*Runner, error) {
	if model == nil {
		return nil, fmt.Errorf("%w: model is required", inference.ErrInvalidArgument)
	}
	if options.Concurrency < 1 || options.Concurrency > 8 {
		return nil, fmt.Errorf("%w: concurrency must be between 1 and 8", inference.ErrInvalidArgument)
	}
	if options.Prompt == "" {
		return nil, fmt.Errorf("%w: prompt is required", inference.ErrInvalidArgument)
	}
	if options.BaseSeed == 0 {
		options.BaseSeed = 42
	}
	sessions := make([]SessionSnapshot, options.Concurrency)
	for index := range sessions {
		sessions[index] = SessionSnapshot{Index: index + 1, Phase: PhaseQueued}
	}
	return &Runner{
		model: model,
		opts:  options,
		snapshot: RunSnapshot{
			Phase:    RunPreparing,
			Sessions: sessions,
		},
		outputs: make([]strings.Builder, options.Concurrency),
		done:    make(chan struct{}),
	}, nil
}

func (r *Runner) Done() <-chan struct{} {
	return r.done
}

func (r *Runner) Snapshot() RunSnapshot {
	r.mu.RLock()
	defer r.mu.RUnlock()
	snapshot := cloneSnapshot(r.snapshot)
	for index := range snapshot.Sessions {
		if output := r.outputs[index].String(); output != "" {
			snapshot.Sessions[index].Output = output
		}
	}
	if !snapshot.StartedAt.IsZero() && !snapshot.Done {
		snapshot.Elapsed = r.elapsedBase + time.Since(snapshot.StartedAt)
		snapshot.MaxNativeBatch = r.model.Capabilities().MaxObservedBatch
		r.calculateTotals(&snapshot)
	}
	return snapshot
}

func (r *Runner) Run(ctx context.Context) (Summary, error) {
	r.operationMu.Lock()
	defer r.operationMu.Unlock()
	r.mu.Lock()
	if r.running {
		r.mu.Unlock()
		return Summary{}, fmt.Errorf("%w: runner may only be started once", inference.ErrBusy)
	}
	r.running = true
	defer close(r.done)
	r.snapshot.StartedAt = time.Now()
	r.snapshot.Phase = RunPreparing
	r.mu.Unlock()

	conversations := make([]*conversation.Conversation, r.opts.Concurrency)
	for index := range conversations {
		value, err := conversation.New(ctx, r.model, r.opts.Conversation)
		if err != nil {
			r.finishPreparationFailure(index, err)
			closeConversations(conversations)
			return r.summary(), fmt.Errorf("create session %d: %w", index+1, err)
		}
		conversations[index] = value
	}
	r.mu.Lock()
	r.conversations = conversations
	r.mu.Unlock()

	r.mu.Lock()
	r.snapshot.Phase = RunRunning
	r.mu.Unlock()

	start := make(chan struct{})
	var wait sync.WaitGroup
	for index, current := range conversations {
		wait.Add(1)
		go func(index int, current *conversation.Conversation) {
			defer wait.Done()
			select {
			case <-ctx.Done():
				r.completeSession(index, inference.GenerateResult{
					FinishReason: inference.FinishCancelled,
				}, ctx.Err())
				return
			case <-start:
			}
			seed := r.opts.BaseSeed + int64(index)
			turn := r.opts.Turn
			turn.Sampling.Seed = &seed
			started := time.Now()
			result, err := current.Turn(
				ctx,
				r.opts.Prompt,
				turn,
				func(event inference.GenerationEvent) error {
					return r.consumeEvent(ctx, index, started, event)
				},
			)
			r.completeSession(index, result, err)
		}(index, current)
	}
	close(start)
	wait.Wait()

	r.mu.Lock()
	r.snapshot.Elapsed = r.elapsedBase + time.Since(r.snapshot.StartedAt)
	r.elapsedBase = r.snapshot.Elapsed
	r.snapshot.MaxNativeBatch = r.model.Capabilities().MaxObservedBatch
	r.snapshot.Done = true
	r.calculateTotals(&r.snapshot)
	switch {
	case errors.Is(ctx.Err(), context.Canceled), errors.Is(ctx.Err(), context.DeadlineExceeded):
		r.snapshot.Phase = RunCancelled
	case sessionErrors(r.snapshot.Sessions) != nil:
		r.snapshot.Phase = RunFailed
	default:
		r.snapshot.Phase = RunCompleted
	}
	final := cloneSnapshot(r.snapshot)
	r.mu.Unlock()

	summary := summaryFromSnapshot(final)
	if err := sessionErrors(final.Sessions); err != nil {
		return summary, err
	}
	if ctx.Err() != nil {
		return summary, ctx.Err()
	}
	return summary, nil
}

func (r *Runner) FollowUp(
	ctx context.Context,
	sessionIndex int,
	prompt string,
) (inference.GenerateResult, error) {
	r.operationMu.Lock()
	defer r.operationMu.Unlock()
	if sessionIndex < 1 || sessionIndex > r.opts.Concurrency {
		return inference.GenerateResult{}, fmt.Errorf(
			"%w: session index must be between 1 and %d",
			inference.ErrInvalidArgument,
			r.opts.Concurrency,
		)
	}
	if strings.TrimSpace(prompt) == "" {
		return inference.GenerateResult{}, fmt.Errorf(
			"%w: follow-up prompt is required",
			inference.ErrInvalidArgument,
		)
	}
	index := sessionIndex - 1
	r.mu.Lock()
	if r.closed {
		r.mu.Unlock()
		return inference.GenerateResult{}, inference.ErrClosed
	}
	if !r.snapshot.Done || len(r.conversations) != r.opts.Concurrency {
		r.mu.Unlock()
		return inference.GenerateResult{}, fmt.Errorf(
			"%w: initial concurrent run is not complete",
			inference.ErrBusy,
		)
	}
	current := r.conversations[index]
	startTokens := r.snapshot.Sessions[index].OutputTokens
	r.outputs[index].WriteString("\n\nYou › ")
	r.outputs[index].WriteString(prompt)
	r.outputs[index].WriteString("\n\nAssistant › ")
	r.snapshot.StartedAt = time.Now()
	r.snapshot.Elapsed = r.elapsedBase
	r.snapshot.Phase = RunFollowing
	r.snapshot.Done = false
	session := &r.snapshot.Sessions[index]
	session.Phase = PhasePrefill
	session.FinishReason = ""
	session.Err = nil
	session.DecodeTPS = 0
	session.Elapsed = 0
	r.mu.Unlock()

	started := time.Now()
	result, err := current.Turn(
		ctx,
		prompt,
		r.opts.Turn,
		func(event inference.GenerationEvent) error {
			return r.consumeFollowUpEvent(ctx, index, started, event)
		},
	)

	r.mu.Lock()
	session = &r.snapshot.Sessions[index]
	if result.Output != "" {
		streamed := session.OutputTokens - startTokens
		if streamed != result.Usage.CompletionTokens {
			session.OutputTokens = startTokens + result.Usage.CompletionTokens
		}
	}
	session.FinishReason = result.FinishReason
	session.DecodeTPS = result.Timings.DecodeTokensPerSecond
	session.Elapsed = time.Since(started)
	session.Err = err
	switch {
	case errors.Is(err, context.Canceled), errors.Is(err, context.DeadlineExceeded),
		result.FinishReason == inference.FinishCancelled:
		session.Phase = PhaseCancelled
		if session.FinishReason == "" {
			session.FinishReason = inference.FinishCancelled
		}
	case err != nil:
		session.Phase = PhaseError
		if session.FinishReason == "" {
			session.FinishReason = inference.FinishError
		}
	default:
		session.Phase = PhaseDone
	}
	r.snapshot.Elapsed = r.elapsedBase + time.Since(r.snapshot.StartedAt)
	r.elapsedBase = r.snapshot.Elapsed
	r.snapshot.MaxNativeBatch = r.model.Capabilities().MaxObservedBatch
	r.snapshot.Done = true
	r.calculateTotals(&r.snapshot)
	switch {
	case errors.Is(err, context.Canceled), errors.Is(err, context.DeadlineExceeded):
		r.snapshot.Phase = RunCancelled
	case err != nil:
		r.snapshot.Phase = RunFailed
	default:
		r.snapshot.Phase = RunCompleted
	}
	r.mu.Unlock()
	return result, err
}

func (r *Runner) consumeFollowUpEvent(
	ctx context.Context,
	index int,
	started time.Time,
	event inference.GenerationEvent,
) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	r.mu.Lock()
	session := &r.snapshot.Sessions[index]
	switch event.Kind {
	case inference.EventStarted:
		session.Phase = PhasePrefill
	case inference.EventPrefillProgress:
		session.Phase = PhasePrefill
		if event.Progress != nil {
			session.PrefillDone = int(event.Progress.Completed)
			session.PrefillTotal = int(event.Progress.Total)
		}
	case inference.EventOutputDelta:
		if event.Delta != nil {
			session.Phase = PhaseGenerating
			r.outputs[index].WriteString(event.Delta.Text)
			if len(event.Delta.Tokens) > 0 {
				session.OutputTokens += len(event.Delta.Tokens)
			} else {
				session.OutputTokens++
			}
			session.Elapsed = time.Since(started)
		}
	}
	r.mu.Unlock()
	return nil
}

func (r *Runner) Close() error {
	r.operationMu.Lock()
	defer r.operationMu.Unlock()
	r.mu.Lock()
	if r.closed {
		r.mu.Unlock()
		return nil
	}
	r.closed = true
	conversations := r.conversations
	r.conversations = nil
	r.mu.Unlock()
	return closeConversations(conversations)
}

func (r *Runner) consumeEvent(
	ctx context.Context,
	index int,
	started time.Time,
	event inference.GenerationEvent,
) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	r.mu.Lock()
	session := &r.snapshot.Sessions[index]
	switch event.Kind {
	case inference.EventStarted:
		session.Phase = PhasePrefill
	case inference.EventPrefillProgress:
		session.Phase = PhasePrefill
		if event.Progress != nil {
			session.PrefillDone = int(event.Progress.Completed)
			session.PrefillTotal = int(event.Progress.Total)
		}
	case inference.EventOutputDelta:
		if event.Delta != nil {
			session.Phase = PhaseGenerating
			r.outputs[index].WriteString(event.Delta.Text)
			if len(event.Delta.Tokens) > 0 {
				session.OutputTokens += len(event.Delta.Tokens)
			} else {
				session.OutputTokens++
			}
			session.Elapsed = time.Since(started)
			if session.Elapsed > 0 {
				session.DecodeTPS = float64(session.OutputTokens) / session.Elapsed.Seconds()
			}
		}
	}
	r.mu.Unlock()
	return nil
}

func (r *Runner) completeSession(index int, result inference.GenerateResult, err error) {
	r.mu.Lock()
	session := &r.snapshot.Sessions[index]
	session.PromptTokens = result.Usage.PromptTokens
	session.PrefillDone = result.Usage.PromptTokens
	session.PrefillTotal = result.Usage.PromptTokens
	if result.Usage.CompletionTokens > 0 {
		session.OutputTokens = result.Usage.CompletionTokens
	}
	if result.Output != "" {
		if r.outputs[index].String() != result.Output {
			r.outputs[index].Reset()
			r.outputs[index].WriteString(result.Output)
		}
		session.Output = result.Output
	}
	session.FinishReason = result.FinishReason
	session.DecodeTPS = result.Timings.DecodeTokensPerSecond
	session.Elapsed = time.Since(r.snapshot.StartedAt)
	session.Err = err
	switch {
	case errors.Is(err, context.Canceled), errors.Is(err, context.DeadlineExceeded),
		result.FinishReason == inference.FinishCancelled:
		session.Phase = PhaseCancelled
		if session.FinishReason == "" {
			session.FinishReason = inference.FinishCancelled
		}
	case err != nil:
		session.Phase = PhaseError
		if session.FinishReason == "" {
			session.FinishReason = inference.FinishError
		}
	default:
		session.Phase = PhaseDone
	}
	r.mu.Unlock()
}

func (r *Runner) finishPreparationFailure(index int, err error) {
	r.mu.Lock()
	r.snapshot.Sessions[index].Phase = PhaseError
	r.snapshot.Sessions[index].Err = err
	for other := index + 1; other < len(r.snapshot.Sessions); other++ {
		r.snapshot.Sessions[other].Phase = PhaseCancelled
	}
	r.snapshot.Elapsed = r.elapsedBase + time.Since(r.snapshot.StartedAt)
	r.elapsedBase = r.snapshot.Elapsed
	r.snapshot.Phase = RunFailed
	r.snapshot.Done = true
	r.calculateTotals(&r.snapshot)
	r.mu.Unlock()
}

func (r *Runner) calculateTotals(snapshot *RunSnapshot) {
	snapshot.TotalTokens = 0
	for _, session := range snapshot.Sessions {
		snapshot.TotalTokens += session.OutputTokens
	}
	if snapshot.Elapsed > 0 {
		snapshot.AggregateTPS = float64(snapshot.TotalTokens) / snapshot.Elapsed.Seconds()
	}
}

func (r *Runner) summary() Summary {
	return summaryFromSnapshot(r.Snapshot())
}

func (r *Runner) Summary() Summary {
	return r.summary()
}

func summaryFromSnapshot(snapshot RunSnapshot) Summary {
	return Summary{
		Sessions:       len(snapshot.Sessions),
		MaxNativeBatch: snapshot.MaxNativeBatch,
		Tokens:         snapshot.TotalTokens,
		Elapsed:        snapshot.Elapsed,
		AggregateTPS:   snapshot.AggregateTPS,
		Cancelled:      snapshot.Phase == RunCancelled,
	}
}

func closeConversations(conversations []*conversation.Conversation) error {
	var closeErrors []error
	for index := len(conversations) - 1; index >= 0; index-- {
		if conversations[index] != nil {
			if err := conversations[index].Close(); err != nil {
				closeErrors = append(closeErrors, err)
			}
		}
	}
	return errors.Join(closeErrors...)
}
