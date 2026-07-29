package continuation

import (
	"context"
	"errors"
	"fmt"
	"strings"
)

var ErrInvalidRequest = errors.New("invalid continuation request")

type Sampling struct {
	Temperature      float32
	TopK             int
	TopP             float32
	PresencePenalty  float32
	FrequencyPenalty float32
	PenaltyDecay     float32
	Seed             *int64
}

type Request struct {
	Model           string
	Prompt          string
	MaxOutputTokens int
	Stops           []string
	Sampling        Sampling
}

type FinishReason string

const (
	FinishStop      FinishReason = "stop"
	FinishLength    FinishReason = "length"
	FinishCancelled FinishReason = "cancelled"
	FinishUnknown   FinishReason = "unknown"
)

type Usage struct {
	PromptTokens     int
	CompletionTokens int
}

type Result struct {
	Text         string
	FinishReason FinishReason
	Usage        Usage
}

type EventKind string

const EventTextDelta EventKind = "text_delta"

type Event struct {
	Kind EventKind
	Text string
}

type EventSink func(Event) error

type Generator interface {
	Continue(context.Context, Request, EventSink) (Result, error)
}

type GenerateFunc func(context.Context, Request, EventSink) (Result, error)

func (f GenerateFunc) Continue(
	ctx context.Context,
	request Request,
	sink EventSink,
) (Result, error) {
	return f(ctx, request, sink)
}

func ValidateRequest(request Request) error {
	if strings.TrimSpace(request.Prompt) == "" {
		return fmt.Errorf("%w: prompt is required", ErrInvalidRequest)
	}
	if request.MaxOutputTokens <= 0 {
		return fmt.Errorf("%w: max output tokens must be positive", ErrInvalidRequest)
	}
	if request.Sampling.Temperature <= 0 {
		return fmt.Errorf("%w: temperature must be positive", ErrInvalidRequest)
	}
	if request.Sampling.TopK <= 0 {
		return fmt.Errorf("%w: top-k must be positive", ErrInvalidRequest)
	}
	if request.Sampling.TopP <= 0 || request.Sampling.TopP > 1 {
		return fmt.Errorf("%w: top-p must be in (0, 1]", ErrInvalidRequest)
	}
	if request.Sampling.PresencePenalty < 0 || request.Sampling.FrequencyPenalty < 0 {
		return fmt.Errorf("%w: repetition penalties cannot be negative", ErrInvalidRequest)
	}
	if request.Sampling.PenaltyDecay <= 0 || request.Sampling.PenaltyDecay > 1 {
		return fmt.Errorf("%w: penalty decay must be in (0, 1]", ErrInvalidRequest)
	}
	for _, stop := range request.Stops {
		if stop == "" {
			return fmt.Errorf("%w: stop sequences cannot be empty", ErrInvalidRequest)
		}
	}
	return nil
}
