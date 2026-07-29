package local

import (
	"context"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type Generator struct {
	session inference.Session
}

func New(session inference.Session) (*Generator, error) {
	if session == nil {
		return nil, fmt.Errorf("%w: local session is required", continuation.ErrInvalidRequest)
	}
	return &Generator{session: session}, nil
}

func (g *Generator) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	if err := continuation.ValidateRequest(request); err != nil {
		return continuation.Result{}, err
	}
	stops := make([]inference.StopSequence, 0, len(request.Stops))
	for _, stop := range request.Stops {
		stops = append(stops, inference.StopSequence{Text: stop})
	}
	result, err := g.session.Generate(ctx, inference.GenerateRequest{
		Raw: &inference.RawInput{Text: request.Prompt},
		Sampling: inference.SamplingOptions{
			Temperature:      request.Sampling.Temperature,
			TopK:             request.Sampling.TopK,
			TopP:             request.Sampling.TopP,
			PresencePenalty:  request.Sampling.PresencePenalty,
			FrequencyPenalty: request.Sampling.FrequencyPenalty,
			PenaltyDecay:     request.Sampling.PenaltyDecay,
			Seed:             request.Sampling.Seed,
		},
		Limits: inference.GenerationLimits{MaxOutputTokens: request.MaxOutputTokens},
		Stops:  stops,
		Commit: inference.CommitOnSuccess,
	}, func(event inference.GenerationEvent) error {
		if sink == nil || event.Kind != inference.EventOutputDelta || event.Delta == nil {
			return nil
		}
		return sink(continuation.Event{
			Kind: continuation.EventTextDelta,
			Text: event.Delta.Text,
		})
	})
	converted := continuation.Result{
		Text:         result.Output,
		FinishReason: finishReason(result.FinishReason),
		Usage: continuation.Usage{
			PromptTokens:     result.Usage.PromptTokens,
			CompletionTokens: result.Usage.CompletionTokens,
		},
	}
	if err != nil {
		return converted, err
	}
	if !result.Committed {
		return converted, fmt.Errorf(
			"%w: local continuation was not committed",
			inference.ErrBackendFailure,
		)
	}
	return converted, nil
}

func finishReason(value inference.FinishReason) continuation.FinishReason {
	switch value {
	case inference.FinishStop:
		return continuation.FinishStop
	case inference.FinishLength:
		return continuation.FinishLength
	case inference.FinishCancelled:
		return continuation.FinishCancelled
	default:
		return continuation.FinishUnknown
	}
}

var _ continuation.Generator = (*Generator)(nil)
