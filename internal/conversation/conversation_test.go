package conversation_test

import (
	"context"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

func TestFiveTurnsCommitCompleteTranscript(t *testing.T) {
	model := newMockModel(t, "answer")
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile:     inference.DefaultPromptProfile(false),
		NativeState: "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	for turn := 0; turn < 5; turn++ {
		result, err := value.Turn(
			context.Background(),
			"question",
			testTurnOptions(),
			func(inference.GenerationEvent) error { return nil },
		)
		if err != nil {
			t.Fatalf("turn %d: %v", turn+1, err)
		}
		if !result.Committed {
			t.Fatalf("turn %d was not committed", turn+1)
		}
	}
	history := value.History()
	if len(history) != 10 {
		t.Fatalf("history messages = %d, want 10", len(history))
	}
	for index, message := range history {
		want := inference.RoleUser
		if index%2 == 1 {
			want = inference.RoleAssistant
		}
		if message.Role != want {
			t.Fatalf("history[%d].Role = %q, want %q", index, message.Role, want)
		}
	}
	if state := value.State(); state.MessageCount != 10 || state.Revision == "" {
		t.Fatalf("unexpected State: %+v", state)
	}
}

func TestSinkFailureRollsBackTurn(t *testing.T) {
	model := newMockModel(t, "partial")
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile: inference.DefaultPromptProfile(false),
	})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	sinkError := errors.New("terminal closed")
	_, err = value.Turn(
		context.Background(),
		"candidate",
		testTurnOptions(),
		func(event inference.GenerationEvent) error {
			if event.Kind == inference.EventOutputDelta {
				return sinkError
			}
			return nil
		},
	)
	if !errors.Is(err, sinkError) {
		t.Fatalf("Turn error = %v, want sink error", err)
	}
	if history := value.History(); len(history) != 0 {
		t.Fatalf("failed turn polluted history: %+v", history)
	}
}

func TestCancellationRollsBackTurn(t *testing.T) {
	started := make(chan struct{}, 1)
	continueGeneration := make(chan struct{})
	model := newMockModelWithConfig(t, mock.Config{
		Output:   "never committed",
		Started:  started,
		Continue: continueGeneration,
	})
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile: inference.DefaultPromptProfile(false),
	})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	ctx, cancel := context.WithCancel(context.Background())
	result := make(chan error, 1)
	go func() {
		_, err := value.Turn(
			ctx,
			"candidate",
			testTurnOptions(),
			func(inference.GenerationEvent) error { return nil },
		)
		result <- err
	}()
	<-started
	cancel()
	if err := <-result; !errors.Is(err, context.Canceled) {
		t.Fatalf("Turn error = %v, want context.Canceled", err)
	}
	if history := value.History(); len(history) != 0 {
		t.Fatalf("cancelled turn polluted history: %+v", history)
	}
}

func TestLogicalSaveLoadAndCorruption(t *testing.T) {
	model := newMockModel(t, "answer")
	profile := inference.DefaultPromptProfile(false)
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile:     profile,
		NativeState: "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	if _, err := value.Turn(
		context.Background(),
		"remember blue whale",
		testTurnOptions(),
		func(inference.GenerationEvent) error { return nil },
	); err != nil {
		t.Fatal(err)
	}
	bundle := filepath.Join(t.TempDir(), "test.rwkv-session")
	if err := value.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	restored, err := conversation.Load(
		context.Background(),
		model,
		bundle,
		conversation.Options{Profile: profile, NativeState: "off"},
		nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	if len(restored.History()) != 2 || restored.State().RecoveryMode != "replay" {
		t.Fatalf("unexpected restored conversation: %+v", restored.State())
	}
	_ = restored.Close()

	current, err := os.ReadFile(filepath.Join(bundle, "CURRENT"))
	if err != nil {
		t.Fatal(err)
	}
	transcriptPath := filepath.Join(
		bundle,
		"revisions",
		string(bytesTrimSpace(current)),
		"transcript.jsonl",
	)
	if err := os.WriteFile(transcriptPath, []byte("{broken"), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := conversation.Load(
		context.Background(),
		model,
		bundle,
		conversation.Options{Profile: profile, NativeState: "off"},
		nil,
	); !errors.Is(err, inference.ErrCorruptState) {
		t.Fatalf("corrupt load error = %v, want ErrCorruptState", err)
	}
}

func TestIncompatibleModelRejected(t *testing.T) {
	first := newMockModelNamed(t, "first", "answer")
	second := newMockModelNamed(t, "second", "answer")
	profile := inference.DefaultPromptProfile(false)
	value, err := conversation.New(context.Background(), first, conversation.Options{Profile: profile})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	bundle := filepath.Join(t.TempDir(), "test.rwkv-session")
	if err := value.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	if _, err := conversation.Load(
		context.Background(),
		second,
		bundle,
		conversation.Options{Profile: profile},
		nil,
	); !errors.Is(err, inference.ErrIncompatibleState) {
		t.Fatalf("load error = %v, want ErrIncompatibleState", err)
	}
}

func TestIncompatibleTokenizerAndTemplateRejected(t *testing.T) {
	base := newMockModel(t, "answer")
	profile := inference.DefaultPromptProfile(false)
	value, err := conversation.New(context.Background(), base, conversation.Options{Profile: profile})
	if err != nil {
		t.Fatal(err)
	}
	defer value.Close()
	bundle := filepath.Join(t.TempDir(), "test.rwkv-session")
	if err := value.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	tokenizerMismatch := &modelInfoOverride{
		Model: base,
		info:  base.Info(),
	}
	tokenizerMismatch.info.TokenizerFingerprint = "sha256:different"
	if _, err := conversation.Load(
		context.Background(),
		tokenizerMismatch,
		bundle,
		conversation.Options{Profile: profile},
		nil,
	); !errors.Is(err, inference.ErrIncompatibleState) {
		t.Fatalf("tokenizer mismatch error = %v, want ErrIncompatibleState", err)
	}
	if _, err := conversation.Load(
		context.Background(),
		base,
		bundle,
		conversation.Options{Profile: inference.DefaultPromptProfile(true)},
		nil,
	); !errors.Is(err, inference.ErrIncompatibleState) {
		t.Fatalf("template mismatch error = %v, want ErrIncompatibleState", err)
	}
}

func TestPromptProfileUpgradeReplaysTranscriptAndKeepsReasoningMode(t *testing.T) {
	model := newMockModel(t, "legacy answer")
	legacy := legacyPromptProfile(true)
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile:     legacy,
		NativeState: "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := value.Turn(
		context.Background(),
		"legacy question",
		testTurnOptions(),
		func(inference.GenerationEvent) error { return nil },
	); err != nil {
		t.Fatal(err)
	}
	oldRevision := value.State().Revision
	bundle := filepath.Join(t.TempDir(), "legacy.rwkv-session")
	if err := value.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	_ = value.Close()

	upgraded, err := conversation.Load(
		context.Background(),
		model,
		bundle,
		conversation.Options{
			NativeState:               "off",
			AllowPromptProfileUpgrade: true,
		},
		nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	defer upgraded.Close()
	if profile := upgraded.Profile(); !profile.Reasoning ||
		profile.TemplateVersion != inference.PromptTemplateVersion {
		t.Fatalf("upgraded profile = %+v", profile)
	}
	state := upgraded.State()
	if state.RecoveryMode != "profile-migration" ||
		state.Revision == oldRevision ||
		state.MessageCount != 2 {
		t.Fatalf("upgraded State = %+v", state)
	}
	if err := upgraded.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	strict, err := conversation.Load(
		context.Background(),
		model,
		bundle,
		conversation.Options{
			Profile:     inference.DefaultPromptProfile(true),
			NativeState: "off",
		},
		nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	defer strict.Close()
	if strict.State().Revision != state.Revision {
		t.Fatalf("saved migrated revision = %q, want %q", strict.State().Revision, state.Revision)
	}
}

func TestPromptProfileUpgradeRejectsReasoningModeChange(t *testing.T) {
	model := newMockModel(t, "answer")
	value, err := conversation.New(context.Background(), model, conversation.Options{
		Profile:     legacyPromptProfile(true),
		NativeState: "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	bundle := filepath.Join(t.TempDir(), "legacy.rwkv-session")
	if err := value.Save(context.Background(), bundle); err != nil {
		t.Fatal(err)
	}
	_ = value.Close()

	_, err = conversation.Load(
		context.Background(),
		model,
		bundle,
		conversation.Options{
			Profile:                   inference.DefaultPromptProfile(false),
			NativeState:               "off",
			AllowPromptProfileUpgrade: true,
		},
		nil,
	)
	if !errors.Is(err, inference.ErrIncompatibleState) ||
		!strings.Contains(err.Error(), "reasoning mode mismatch") {
		t.Fatalf("load error = %v, want reasoning mode mismatch", err)
	}
}

func legacyPromptProfile(reasoning bool) inference.PromptProfile {
	return inference.PromptProfile{
		TemplateID:      inference.PromptTemplateID,
		TemplateVersion: 1,
		ProfileHash:     "sha256:legacy-profile",
		Reasoning:       reasoning,
		SpaceAfterRoles: true,
		BOS:             "<|bos|>",
		EOS:             "\n\n",
	}
}

func testTurnOptions() conversation.TurnOptions {
	return conversation.TurnOptions{
		Sampling: inference.SamplingOptions{Temperature: 1, TopK: 1, TopP: 1},
		Limits:   inference.GenerationLimits{MaxOutputTokens: 16},
	}
}

func newMockModel(t *testing.T, output string) inference.Model {
	return newMockModelNamed(t, "model", output)
}

func newMockModelNamed(t *testing.T, name, output string) inference.Model {
	return newMockModelWithBackend(t, name, mock.New(mock.Config{Output: output}))
}

func newMockModelWithConfig(t *testing.T, config mock.Config) inference.Model {
	return newMockModelWithBackend(t, "model", mock.New(config))
}

func newMockModelWithBackend(t *testing.T, name string, backend inference.Backend) inference.Model {
	t.Helper()
	model, err := backend.LoadModel(context.Background(), inference.LoadRequest{
		Source: inference.ModelSource{Path: name},
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = model.Close() })
	return model
}

func bytesTrimSpace(value []byte) []byte {
	start, end := 0, len(value)
	for start < end && (value[start] == ' ' || value[start] == '\n' || value[start] == '\r' || value[start] == '\t') {
		start++
	}
	for end > start && (value[end-1] == ' ' || value[end-1] == '\n' || value[end-1] == '\r' || value[end-1] == '\t') {
		end--
	}
	return value[start:end]
}

type modelInfoOverride struct {
	inference.Model
	info inference.ModelInfo
}

func (m *modelInfoOverride) Info() inference.ModelInfo { return m.info }
