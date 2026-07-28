package conversation

import (
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestTranscriptRevisionIsDeterministicTurnChain(t *testing.T) {
	model := inference.ModelInfo{
		Fingerprint:          "sha256:model",
		TokenizerFingerprint: "sha256:tokenizer",
	}
	profile := inference.DefaultPromptProfile(false)
	messages := []inference.Message{
		inference.TextMessage(inference.RoleUser, "one"),
		inference.TextMessage(inference.RoleAssistant, "first"),
		inference.TextMessage(inference.RoleUser, "two"),
		inference.TextMessage(inference.RoleAssistant, "second"),
	}
	first, err := calculateTranscriptRevision(messages, model, profile, "")
	if err != nil {
		t.Fatal(err)
	}
	second, err := calculateTranscriptRevision(messages, model, profile, "")
	if err != nil {
		t.Fatal(err)
	}
	if first != second || first == "" {
		t.Fatalf("revision is not deterministic: %q != %q", first, second)
	}
	changed := append([]inference.Message(nil), messages...)
	changed[3] = inference.TextMessage(inference.RoleAssistant, "changed")
	third, err := calculateTranscriptRevision(changed, model, profile, "")
	if err != nil {
		t.Fatal(err)
	}
	if third == first {
		t.Fatal("changed committed turn did not change revision")
	}
}
