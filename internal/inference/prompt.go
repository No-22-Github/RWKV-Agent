package inference

import (
	"crypto/sha256"
	"errors"
	"fmt"
	"strings"
)

const (
	PromptTemplateID      = "rwkv-g1-chat"
	PromptTemplateVersion = 1
)

func DefaultPromptProfile(reasoning bool) PromptProfile {
	canonical := fmt.Sprintf(
		"%s\x00%d\x00%t\x00%t\x00%t\x00%s\x00%s",
		PromptTemplateID,
		PromptTemplateVersion,
		reasoning,
		true,
		false,
		"<|bos|>",
		"\n\n",
	)
	return PromptProfile{
		TemplateID:      PromptTemplateID,
		TemplateVersion: PromptTemplateVersion,
		ProfileHash:     fmt.Sprintf("sha256:%x", sha256.Sum256([]byte(canonical))),
		Reasoning:       reasoning,
		SpaceAfterRoles: true,
		BOS:             "<|bos|>",
		EOS:             "\n\n",
	}
}

func CompileGeneratePrompt(request GenerateRequest) (string, error) {
	if err := validateInput(request.Messages, request.Raw); err != nil {
		return "", err
	}
	if request.Raw != nil {
		return request.Raw.Text, nil
	}

	var prompt strings.Builder
	for _, message := range request.Messages {
		text, err := messageText(message)
		if err != nil {
			return "", err
		}
		role, err := promptRole(message.Role)
		if err != nil {
			return "", err
		}
		fmt.Fprintf(&prompt, "%s: %s\n\n", role, text)
	}
	prompt.WriteString("Assistant:")

	formatted := prompt.String()
	if request.Prompt.Reasoning {
		formatted = "<|bos|>" + formatted + " <think>\n</think>"
	}
	return formatted, nil
}

func CompileCommittedPrompt(messages []Message, options PromptOptions) (string, error) {
	if err := validateInput(messages, nil); err != nil {
		return "", err
	}
	var prompt strings.Builder
	for _, message := range messages {
		text, err := messageText(message)
		if err != nil {
			return "", err
		}
		role, err := promptRole(message.Role)
		if err != nil {
			return "", err
		}
		fmt.Fprintf(&prompt, "%s: %s\n\n", role, text)
	}
	formatted := prompt.String()
	if options.Reasoning {
		formatted = "<|bos|>" + formatted
	}
	return formatted, nil
}

func CompileTokenCountPrompt(request TokenCountRequest) (string, error) {
	return CompileGeneratePrompt(GenerateRequest{
		Messages: request.Messages,
		Raw:      request.Raw,
		Prompt:   request.Prompt,
	})
}

func ValidateGenerateRequest(request GenerateRequest) error {
	if _, err := CompileGeneratePrompt(request); err != nil {
		return err
	}
	if request.Limits.MaxOutputTokens <= 0 {
		return fmt.Errorf("%w: max output tokens must be positive", ErrInvalidArgument)
	}
	if request.Sampling.Temperature <= 0 {
		return fmt.Errorf("%w: temperature must be positive", ErrInvalidArgument)
	}
	if request.Sampling.TopK <= 0 {
		return fmt.Errorf("%w: top-k must be positive", ErrInvalidArgument)
	}
	if request.Sampling.TopP <= 0 || request.Sampling.TopP > 1 {
		return fmt.Errorf("%w: top-p must be in (0, 1]", ErrInvalidArgument)
	}
	switch request.Commit {
	case "", CommitOnSuccess, CommitPartial:
	default:
		return fmt.Errorf("%w: unknown commit policy %q", ErrInvalidArgument, request.Commit)
	}
	return nil
}

func validateInput(messages []Message, raw *RawInput) error {
	if raw != nil && len(messages) != 0 {
		return fmt.Errorf("%w: messages and raw input are mutually exclusive", ErrInvalidArgument)
	}
	if raw != nil {
		if raw.Text == "" {
			return fmt.Errorf("%w: raw input must not be empty", ErrInvalidArgument)
		}
		return nil
	}
	if len(messages) == 0 {
		return fmt.Errorf("%w: messages or raw input are required", ErrInvalidArgument)
	}
	return nil
}

func messageText(message Message) (string, error) {
	if len(message.Parts) == 0 {
		return "", fmt.Errorf("%w: message has no content", ErrInvalidArgument)
	}
	var text strings.Builder
	for _, part := range message.Parts {
		if part.Kind != ContentText {
			return "", fmt.Errorf("%w: content kind %q", ErrUnsupported, part.Kind)
		}
		text.WriteString(part.Text)
	}
	if text.Len() == 0 {
		return "", fmt.Errorf("%w: message text must not be empty", ErrInvalidArgument)
	}
	return text.String(), nil
}

func promptRole(role Role) (string, error) {
	switch role {
	case RoleSystem:
		return "System", nil
	case RoleUser:
		return "User", nil
	case RoleAssistant:
		return "Assistant", nil
	case RoleTool:
		return "Tool", nil
	default:
		return "", errors.Join(ErrInvalidArgument, fmt.Errorf("unknown message role %q", role))
	}
}
