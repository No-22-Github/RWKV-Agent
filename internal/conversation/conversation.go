package conversation

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"sync"

	"github.com/no22/RWKV-Agent/internal/conversation/store"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type Options struct {
	Profile                   inference.PromptProfile
	InitialStateFingerprint   string
	NativeState               string
	AllowPromptProfileUpgrade bool
}

type TurnOptions struct {
	Sampling inference.SamplingOptions
	Limits   inference.GenerationLimits
}

type State struct {
	Revision                  string
	TranscriptHash            string
	Status                    string
	MessageCount              int
	CommittedPrefixTokenCount int
	NativeRevision            string
	NativeSnapshot            bool
	RecoveryMode              string
	DirtyReason               string
}

type Conversation struct {
	mu                      sync.Mutex
	model                   inference.Model
	session                 inference.Session
	tokenizer               inference.Tokenizer
	modelInfo               inference.ModelInfo
	profile                 inference.PromptProfile
	initialStateFingerprint string
	nativeStateMode         string
	transcript              []inference.Message
	revision                string
	transcriptHash          string
	recoveryMode            string
}

func New(ctx context.Context, model inference.Model, options Options) (*Conversation, error) {
	if model == nil {
		return nil, fmt.Errorf("%w: model is required", inference.ErrInvalidArgument)
	}
	if options.Profile.TemplateID == "" {
		options.Profile = inference.DefaultPromptProfile(false)
	}
	if options.NativeState == "" {
		options.NativeState = "auto"
	}
	session, err := model.NewSession(ctx, inference.SessionOptions{})
	if err != nil {
		return nil, err
	}
	tokenizer, ok := session.(inference.Tokenizer)
	if !ok {
		_ = session.Close()
		return nil, fmt.Errorf("%w: backend does not expose exact token encoding", inference.ErrUnsupported)
	}
	revision, err := calculateRevision(
		"",
		nil,
		model.Info(),
		options.Profile,
		options.InitialStateFingerprint,
	)
	if err != nil {
		_ = session.Close()
		return nil, err
	}
	hash, err := transcriptHash(nil)
	if err != nil {
		_ = session.Close()
		return nil, err
	}
	return &Conversation{
		model:                   model,
		session:                 session,
		tokenizer:               tokenizer,
		modelInfo:               model.Info(),
		profile:                 options.Profile,
		initialStateFingerprint: options.InitialStateFingerprint,
		nativeStateMode:         options.NativeState,
		revision:                revision,
		transcriptHash:          hash,
		recoveryMode:            "new",
	}, nil
}

func (c *Conversation) Turn(
	ctx context.Context,
	userText string,
	options TurnOptions,
	sink inference.EventSink,
) (inference.GenerateResult, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	if userText == "" {
		return inference.GenerateResult{}, fmt.Errorf("%w: user message must not be empty", inference.ErrInvalidArgument)
	}
	if sink == nil {
		return inference.GenerateResult{}, fmt.Errorf("%w: event sink is required", inference.ErrInvalidArgument)
	}
	if err := c.ensureClean(ctx, nil); err != nil {
		return inference.GenerateResult{}, err
	}
	candidate := appendMessages(c.transcript, inference.TextMessage(inference.RoleUser, userText))
	result, err := c.session.Generate(ctx, inference.GenerateRequest{
		Messages: candidate,
		Prompt:   inference.PromptOptions{Reasoning: c.profile.Reasoning},
		Sampling: options.Sampling,
		Limits:   options.Limits,
		Commit:   inference.CommitOnSuccess,
	}, sink)
	if err != nil {
		return result, err
	}
	if !result.Committed || result.Output == "" {
		return result, fmt.Errorf("%w: backend did not produce a clean committed result", inference.ErrBackendFailure)
	}
	candidate = appendMessages(candidate, inference.TextMessage(inference.RoleAssistant, result.Output))
	if err := c.syncCommitted(ctx, candidate, nil); err != nil {
		return result, fmt.Errorf("align committed transcript: %w", err)
	}
	revision, err := calculateRevision(
		c.revision,
		candidate[len(candidate)-2:],
		c.modelInfo,
		c.profile,
		c.initialStateFingerprint,
	)
	if err != nil {
		return result, err
	}
	hash, err := transcriptHash(candidate)
	if err != nil {
		return result, err
	}
	c.transcript = candidate
	c.revision = revision
	c.transcriptHash = hash
	c.recoveryMode = "native"
	result.StateRevision = revision
	result.Committed = true
	return result, nil
}

func (c *Conversation) ensureClean(ctx context.Context, progress inference.ProgressSink) error {
	state := c.session.StateInfo()
	if state.Status != "dirty" {
		return nil
	}
	return c.syncCommitted(ctx, c.transcript, progress)
}

func (c *Conversation) syncCommitted(
	ctx context.Context,
	messages []inference.Message,
	progress inference.ProgressSink,
) error {
	if len(messages) == 0 {
		return c.session.Reset(ctx)
	}
	text, err := inference.CompileCommittedPrompt(
		messages,
		inference.PromptOptions{Reasoning: c.profile.Reasoning},
	)
	if err != nil {
		return err
	}
	tokens, err := c.tokenizer.Encode(ctx, text)
	if err != nil {
		return err
	}
	_, err = c.session.Prefill(ctx, inference.PrefillRequest{Tokens: tokens}, progress)
	return err
}

func (c *Conversation) Reset(ctx context.Context) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if err := c.session.Reset(ctx); err != nil {
		return err
	}
	revision, err := calculateRevision(
		"",
		nil,
		c.modelInfo,
		c.profile,
		c.initialStateFingerprint,
	)
	if err != nil {
		return err
	}
	hash, err := transcriptHash(nil)
	if err != nil {
		return err
	}
	c.transcript = nil
	c.revision = revision
	c.transcriptHash = hash
	c.recoveryMode = "reset"
	return nil
}

func (c *Conversation) History() []inference.Message {
	c.mu.Lock()
	defer c.mu.Unlock()
	return appendMessages(nil, c.transcript...)
}

func (c *Conversation) State() State {
	c.mu.Lock()
	defer c.mu.Unlock()
	nativeState := c.session.StateInfo()
	return State{
		Revision:                  c.revision,
		TranscriptHash:            c.transcriptHash,
		Status:                    nativeState.Status,
		MessageCount:              len(c.transcript),
		CommittedPrefixTokenCount: nativeState.CommittedPrefixTokenCount,
		NativeRevision:            nativeState.NativeRevision,
		NativeSnapshot:            nativeState.NativeSnapshot,
		RecoveryMode:              c.recoveryMode,
		DirtyReason:               nativeState.DirtyReason,
	}
}

func (c *Conversation) Profile() inference.PromptProfile {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.profile
}

func (c *Conversation) Save(ctx context.Context, path string) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if err := c.ensureClean(ctx, nil); err != nil {
		return fmt.Errorf("rebuild before save: %w", err)
	}
	var stateData []byte
	var descriptor inference.StateDescriptor
	if c.nativeStateMode != "off" && c.model.Capabilities().StateExport.Available {
		var buffer bytes.Buffer
		value, err := c.session.ExportState(ctx, &buffer, inference.ExportStateOptions{})
		if err != nil {
			if c.nativeStateMode == "required" {
				return err
			}
		} else {
			stateData = buffer.Bytes()
			descriptor = value
		}
	}
	return store.Save(path, store.Snapshot{
		SchemaVersion:           SchemaVersion,
		Revision:                c.revision,
		TranscriptHash:          c.transcriptHash,
		Model:                   c.modelInfo,
		Profile:                 c.profile,
		InitialStateFingerprint: c.initialStateFingerprint,
		RuntimeABIVersion:       1,
		RWKVMobileCommit:        "a9a66e8bea2a708d6ca14ccb9bb46c721a5b7fdd",
		Transcript:              appendMessages(nil, c.transcript...),
		StateDescriptor:         descriptor,
		NativeState:             stateData,
	})
}

func Load(
	ctx context.Context,
	model inference.Model,
	path string,
	options Options,
	progress inference.ProgressSink,
) (*Conversation, error) {
	snapshot, err := store.Load(path)
	if err != nil {
		return nil, err
	}
	actualTranscriptHash, err := transcriptHash(snapshot.Transcript)
	if err != nil {
		return nil, err
	}
	if actualTranscriptHash != snapshot.TranscriptHash {
		return nil, fmt.Errorf("%w: canonical transcript hash mismatch", inference.ErrCorruptState)
	}
	if options.Profile.TemplateID == "" {
		options.Profile = inference.DefaultPromptProfile(snapshot.Profile.Reasoning)
	}
	if options.NativeState == "" {
		options.NativeState = "auto"
	}
	profileUpgraded, err := validateCompatibility(model.Info(), options, snapshot)
	if err != nil {
		return nil, err
	}
	sourceRevision, err := calculateTranscriptRevision(
		snapshot.Transcript,
		model.Info(),
		snapshot.Profile,
		options.InitialStateFingerprint,
	)
	if err != nil {
		return nil, err
	}
	if sourceRevision != snapshot.Revision {
		return nil, fmt.Errorf("%w: logical revision mismatch", inference.ErrCorruptState)
	}
	targetRevision := sourceRevision
	if profileUpgraded {
		targetRevision, err = calculateTranscriptRevision(
			snapshot.Transcript,
			model.Info(),
			options.Profile,
			options.InitialStateFingerprint,
		)
		if err != nil {
			return nil, err
		}
	}
	conversation, err := New(ctx, model, options)
	if err != nil {
		return nil, err
	}
	restored := false
	if len(snapshot.NativeState) == 0 && options.NativeState == "required" {
		_ = conversation.Close()
		return nil, fmt.Errorf("%w: required native State snapshot is missing", inference.ErrIncompatibleState)
	}
	if !profileUpgraded &&
		len(snapshot.NativeState) > 0 &&
		options.NativeState != "off" &&
		model.Capabilities().StateImport.Available {
		_, importErr := conversation.session.ImportState(
			ctx,
			bytes.NewReader(snapshot.NativeState),
			inference.ImportStateOptions{Descriptor: snapshot.StateDescriptor},
		)
		if importErr == nil {
			restored = true
			conversation.recoveryMode = "native"
		} else if options.NativeState == "required" {
			_ = conversation.Close()
			return nil, importErr
		}
	}
	conversation.transcript = appendMessages(nil, snapshot.Transcript...)
	conversation.revision = targetRevision
	conversation.transcriptHash = snapshot.TranscriptHash
	if !restored {
		if err := conversation.session.Reset(ctx); err != nil {
			_ = conversation.Close()
			return nil, err
		}
		if err := conversation.syncCommitted(ctx, conversation.transcript, progress); err != nil {
			_ = conversation.Close()
			return nil, err
		}
		if profileUpgraded {
			conversation.recoveryMode = "profile-migration"
		} else {
			conversation.recoveryMode = "replay"
		}
	} else if err := conversation.syncCommitted(ctx, conversation.transcript, progress); err != nil {
		_ = conversation.Close()
		return nil, err
	}
	return conversation, nil
}

func validateCompatibility(
	model inference.ModelInfo,
	options Options,
	snapshot store.Snapshot,
) (bool, error) {
	if snapshot.SchemaVersion != SchemaVersion {
		return false, fmt.Errorf("%w: session schema %d", inference.ErrIncompatibleState, snapshot.SchemaVersion)
	}
	if snapshot.Model.Fingerprint != model.Fingerprint {
		return false, fmt.Errorf("%w: model fingerprint mismatch", inference.ErrIncompatibleState)
	}
	if snapshot.Model.TokenizerFingerprint != model.TokenizerFingerprint {
		return false, fmt.Errorf("%w: tokenizer fingerprint mismatch", inference.ErrIncompatibleState)
	}
	if snapshot.InitialStateFingerprint != options.InitialStateFingerprint {
		return false, fmt.Errorf("%w: Initial State fingerprint mismatch", inference.ErrIncompatibleState)
	}
	if profilesMatch(snapshot.Profile, options.Profile) {
		return false, nil
	}
	if !options.AllowPromptProfileUpgrade {
		return false, fmt.Errorf("%w: prompt profile mismatch", inference.ErrIncompatibleState)
	}
	if snapshot.Profile.TemplateID != options.Profile.TemplateID {
		return false, fmt.Errorf("%w: prompt template mismatch", inference.ErrIncompatibleState)
	}
	if snapshot.Profile.Reasoning != options.Profile.Reasoning {
		return false, fmt.Errorf("%w: reasoning mode mismatch", inference.ErrIncompatibleState)
	}
	current := inference.DefaultPromptProfile(options.Profile.Reasoning)
	if !profilesMatch(current, options.Profile) ||
		snapshot.Profile.TemplateVersion <= 0 ||
		snapshot.Profile.TemplateVersion >= options.Profile.TemplateVersion {
		return false, fmt.Errorf("%w: prompt profile mismatch", inference.ErrIncompatibleState)
	}
	if options.NativeState == "required" {
		return false, fmt.Errorf(
			"%w: prompt profile upgrade requires transcript replay",
			inference.ErrIncompatibleState,
		)
	}
	return true, nil
}

func profilesMatch(left, right inference.PromptProfile) bool {
	return left.TemplateID == right.TemplateID &&
		left.TemplateVersion == right.TemplateVersion &&
		left.ProfileHash == right.ProfileHash
}

func (c *Conversation) ReplaceWith(other *Conversation) error {
	if other == nil {
		return fmt.Errorf("%w: replacement conversation is nil", inference.ErrInvalidArgument)
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	other.mu.Lock()
	defer other.mu.Unlock()
	oldSession := c.session
	c.session = other.session
	c.tokenizer = other.tokenizer
	c.modelInfo = other.modelInfo
	c.profile = other.profile
	c.initialStateFingerprint = other.initialStateFingerprint
	c.nativeStateMode = other.nativeStateMode
	c.transcript = other.transcript
	c.revision = other.revision
	c.transcriptHash = other.transcriptHash
	c.recoveryMode = other.recoveryMode
	other.session = nil
	other.tokenizer = nil
	if oldSession != nil {
		return oldSession.Close()
	}
	return nil
}

func (c *Conversation) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.session == nil {
		return nil
	}
	err := c.session.Close()
	c.session = nil
	c.tokenizer = nil
	return err
}

func appendMessages(base []inference.Message, values ...inference.Message) []inference.Message {
	result := make([]inference.Message, len(base), len(base)+len(values))
	copy(result, base)
	for _, message := range values {
		copyMessage := message
		copyMessage.Parts = append([]inference.ContentPart(nil), message.Parts...)
		result = append(result, copyMessage)
	}
	return result
}

var _ io.Closer = (*Conversation)(nil)
