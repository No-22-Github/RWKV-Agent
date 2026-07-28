package conversation

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/inference"
)

const SchemaVersion = 1

type canonicalPart struct {
	Kind inference.ContentKind `json:"kind"`
	Text string                `json:"text"`
}

type canonicalMessage struct {
	Role       inference.Role  `json:"role"`
	Name       string          `json:"name,omitempty"`
	ToolCallID string          `json:"tool_call_id,omitempty"`
	Parts      []canonicalPart `json:"parts"`
}

func canonicalMessages(messages []inference.Message) ([]byte, error) {
	canonical := make([]canonicalMessage, len(messages))
	for index, message := range messages {
		if message.Role != inference.RoleSystem &&
			message.Role != inference.RoleUser &&
			message.Role != inference.RoleAssistant &&
			message.Role != inference.RoleTool {
			return nil, fmt.Errorf("%w: invalid transcript role %q", inference.ErrInvalidArgument, message.Role)
		}
		canonical[index] = canonicalMessage{
			Role:       message.Role,
			Name:       message.Name,
			ToolCallID: message.ToolCallID,
			Parts:      make([]canonicalPart, len(message.Parts)),
		}
		for partIndex, part := range message.Parts {
			if part.Kind != inference.ContentText {
				return nil, fmt.Errorf("%w: unsupported transcript content %q", inference.ErrUnsupported, part.Kind)
			}
			canonical[index].Parts[partIndex] = canonicalPart{Kind: part.Kind, Text: part.Text}
		}
	}
	return json.Marshal(canonical)
}

func transcriptHash(messages []inference.Message) (string, error) {
	canonical, err := canonicalMessages(messages)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(canonical)
	return "sha256:" + hex.EncodeToString(sum[:]), nil
}

func calculateRevision(
	parent string,
	messages []inference.Message,
	model inference.ModelInfo,
	profile inference.PromptProfile,
	initialStateFingerprint string,
) (string, error) {
	canonical, err := canonicalMessages(messages)
	if err != nil {
		return "", err
	}
	digest := sha256.New()
	fmt.Fprintf(
		digest,
		"%d\x00%s\x00%s\x00%s\x00%s\x00%d\x00%s\x00%s\x00",
		SchemaVersion,
		parent,
		model.Fingerprint,
		model.TokenizerFingerprint,
		profile.TemplateID,
		profile.TemplateVersion,
		profile.ProfileHash,
		initialStateFingerprint,
	)
	digest.Write(canonical)
	return fmt.Sprintf("sha256:%x", digest.Sum(nil)), nil
}

func calculateTranscriptRevision(
	messages []inference.Message,
	model inference.ModelInfo,
	profile inference.PromptProfile,
	initialStateFingerprint string,
) (string, error) {
	revision, err := calculateRevision(
		"",
		nil,
		model,
		profile,
		initialStateFingerprint,
	)
	if err != nil {
		return "", err
	}
	if len(messages)%2 != 0 {
		return "", fmt.Errorf("%w: transcript has an incomplete turn", inference.ErrCorruptState)
	}
	for index := 0; index < len(messages); index += 2 {
		if messages[index].Role != inference.RoleUser ||
			messages[index+1].Role != inference.RoleAssistant {
			return "", fmt.Errorf("%w: transcript turn roles are invalid", inference.ErrCorruptState)
		}
		revision, err = calculateRevision(
			revision,
			messages[index:index+2],
			model,
			profile,
			initialStateFingerprint,
		)
		if err != nil {
			return "", err
		}
	}
	return revision, nil
}
