package continuation

import (
	"errors"
	"testing"
)

func TestValidateRequest(t *testing.T) {
	t.Parallel()
	valid := Request{
		Prompt:          "User: task\n\nAssistant:",
		MaxOutputTokens: 128,
		Sampling: Sampling{
			Temperature:  1,
			TopK:         1,
			TopP:         1,
			PenaltyDecay: 0.99,
		},
	}
	if err := ValidateRequest(valid); err != nil {
		t.Fatal(err)
	}
	for name, mutate := range map[string]func(*Request){
		"prompt":      func(value *Request) { value.Prompt = "" },
		"max tokens":  func(value *Request) { value.MaxOutputTokens = 0 },
		"temperature": func(value *Request) { value.Sampling.Temperature = 0 },
		"top k":       func(value *Request) { value.Sampling.TopK = 0 },
		"top p":       func(value *Request) { value.Sampling.TopP = 2 },
		"decay":       func(value *Request) { value.Sampling.PenaltyDecay = 0 },
		"stop":        func(value *Request) { value.Stops = []string{""} },
	} {
		t.Run(name, func(t *testing.T) {
			value := valid
			mutate(&value)
			if err := ValidateRequest(value); !errors.Is(err, ErrInvalidRequest) {
				t.Fatalf("error = %v, want ErrInvalidRequest", err)
			}
		})
	}
}
