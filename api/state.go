package api

import (
	"context"
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

// RemoteState describes one state held by an rwkv_lightning CUDA deployment.
// The deployment keeps uploads in a process-local temporary directory, so the
// list is shared by every client of that deployment and empties on restart.
type RemoteState struct {
	ID          string `json:"id"`
	Filename    string `json:"filename"`
	SizeBytes   int64  `json:"sizeBytes"`
	TensorCount int    `json:"tensorCount"`
	// Created is the server's upload time in Unix seconds.
	Created int64 `json:"created"`
}

// SupportsUploadedState reports whether the provider honors Config.StateID.
// Python Lightning's raw route rejects state_id; Chat Completions and local
// inference have no uploaded-state concept yet.
func SupportsUploadedState(kind Provider) bool {
	return kind == ProviderRWKVLightningCUDA
}

// ListStates returns every state currently held by the configured deployment.
func (s *Service) ListStates(ctx context.Context, config Config) ([]RemoteState, error) {
	client, err := stateClient(config)
	if err != nil {
		return nil, err
	}
	listed, err := client.ListStates(ctx)
	if err != nil {
		return nil, fmt.Errorf("list states: %w", err)
	}
	states := make([]RemoteState, 0, len(listed))
	for _, item := range listed {
		states = append(states, remoteState(item))
	}
	return states, nil
}

// UploadState uploads a serialized RWKV state file (.pth) and returns the
// server-assigned record. progress, when non-nil, receives body bytes sent.
func (s *Service) UploadState(ctx context.Context, config Config, path string, progress func(sent, total int64)) (RemoteState, error) {
	if strings.TrimSpace(path) == "" {
		return RemoteState{}, fmt.Errorf("state file path is required")
	}
	client, err := stateClient(config)
	if err != nil {
		return RemoteState{}, err
	}
	uploaded, err := client.UploadStateWithProgress(ctx, path, progress)
	if err != nil {
		return RemoteState{}, fmt.Errorf("upload state: %w", err)
	}
	return remoteState(uploaded), nil
}

// DeleteState removes a state from the deployment for every client using it.
func (s *Service) DeleteState(ctx context.Context, config Config, id string) error {
	client, err := stateClient(config)
	if err != nil {
		return err
	}
	if err := client.DeleteState(ctx, id); err != nil {
		return fmt.Errorf("delete state: %w", err)
	}
	return nil
}

func stateClient(config Config) (*rwkvlightning.Client, error) {
	if !SupportsUploadedState(config.Provider) {
		return nil, fmt.Errorf("uploaded states require the %s provider", ProviderRWKVLightningCUDA)
	}
	headers, _, err := validatedHeaders(config.Headers)
	if err != nil {
		return nil, err
	}
	password := strings.TrimSpace(config.Password)
	if password == "" {
		password = strings.TrimSpace(config.APIKey)
	}
	return rwkvlightning.New(rwkvlightning.Config{
		Endpoint: strings.TrimSpace(config.Endpoint),
		Password: password,
		Headers:  headers,
	})
}

func remoteState(info rwkvlightning.StateInfo) RemoteState {
	return RemoteState{
		ID: info.StateID, Filename: info.Filename, SizeBytes: info.SizeBytes,
		TensorCount: info.TensorCount, Created: info.Created,
	}
}
