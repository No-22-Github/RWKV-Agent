package converter

import (
	"errors"
	"testing"
)

func TestConvertValidatesOptions(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		options Options
		want    string
	}{
		{name: "input", options: Options{}, want: "input .pth path is required"},
		{name: "output", options: Options{InputPath: "model.pth"}, want: "output model directory is required"},
		{
			name: "tokenizer",
			options: Options{
				InputPath:  "model.pth",
				OutputPath: "model",
			},
			want: "tokenizer path is required",
		},
		{
			name: "precision",
			options: Options{
				InputPath:     "model.pth",
				OutputPath:    "model",
				TokenizerPath: "vocab.txt",
				Precision:     "int4",
			},
			want: "precision must be bf16, fp16, or fp32",
		},
	}

	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			err := Convert(test.options)
			if err == nil || err.Error() != test.want {
				t.Fatalf("Convert() error = %v, want %q", err, test.want)
			}
		})
	}
}

func TestStubReportsUnavailable(t *testing.T) {
	if Available() {
		t.Skip("native converter build")
	}
	err := Convert(Options{
		InputPath:     "model.pth",
		OutputPath:    "model",
		TokenizerPath: "vocab.txt",
		Precision:     "bf16",
	})
	if !errors.Is(err, ErrUnavailable) {
		t.Fatalf("Convert() error = %v, want ErrUnavailable", err)
	}
}
