package converter

import "errors"

var ErrUnavailable = errors.New("native model converter is unavailable in this build")

type Options struct {
	InputPath     string
	OutputPath    string
	TokenizerPath string
	Precision     string
	Overwrite     bool
}

func Available() bool {
	return platformAvailable()
}

func Convert(options Options) error {
	if options.InputPath == "" {
		return errors.New("input .pth path is required")
	}
	if options.OutputPath == "" {
		return errors.New("output model directory is required")
	}
	if options.TokenizerPath == "" {
		return errors.New("tokenizer path is required")
	}
	switch options.Precision {
	case "bf16", "fp16", "fp32":
	default:
		return errors.New("precision must be bf16, fp16, or fp32")
	}
	return platformConvert(options)
}
