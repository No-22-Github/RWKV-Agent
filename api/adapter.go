package api

import (
	"context"
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

// RemoteAdapter is one registered version of a MiSS adapter on an
// rwkv_lightning CUDA deployment. Registrations live in the server's RAM:
// they are shared by every client and vanish when the server restarts.
type RemoteAdapter struct {
	ID string `json:"id"`
	// Version is the content SHA-256; the newest version of an ID is the one
	// generations bind when they name only the ID.
	Version         string  `json:"version"`
	Rank            int     `json:"rank,omitempty"`
	Alpha           float64 `json:"alpha,omitempty"`
	Scale           float64 `json:"scale,omitempty"`
	BaseFingerprint string  `json:"baseFingerprint,omitempty"`
	DType           string  `json:"dtype,omitempty"`
}

// ErrAdaptersUnsupported marks a deployment too old to serve MiSS adapters;
// it would ignore adapter_id and silently run the base model.
var ErrAdaptersUnsupported = rwkvlightning.ErrAdaptersUnsupported

// SupportsAdapter reports whether the provider honors Config.AdapterID. It is
// the same deployment family that serves uploaded states.
func SupportsAdapter(kind Provider) bool {
	return kind == ProviderRWKVLightningCUDA
}

// ListAdapters returns every adapter version registered on the deployment.
func (s *Service) ListAdapters(ctx context.Context, config Config) ([]RemoteAdapter, error) {
	client, err := adapterClient(config)
	if err != nil {
		return nil, err
	}
	listed, err := client.ListAdapters(ctx)
	if err != nil {
		return nil, fmt.Errorf("list adapters: %w", err)
	}
	adapters := make([]RemoteAdapter, 0, len(listed))
	for _, item := range listed {
		adapters = append(adapters, remoteAdapter(item))
	}
	return adapters, nil
}

// RegisterAdapterPath registers a MiSS package already on the inference host;
// path is resolved by the server. It returns the registered content version.
func (s *Service) RegisterAdapterPath(ctx context.Context, config Config, id, path string) (string, error) {
	client, err := adapterClient(config)
	if err != nil {
		return "", err
	}
	version, err := client.RegisterAdapterPath(ctx, id, path)
	if err != nil {
		return "", fmt.Errorf("register adapter: %w", err)
	}
	return version, nil
}

// UploadAdapter uploads a local MiSS package and registers it under id.
func (s *Service) UploadAdapter(ctx context.Context, config Config, id, path string, progress func(sent, total int64)) (string, error) {
	if strings.TrimSpace(path) == "" {
		return "", fmt.Errorf("adapter file path is required")
	}
	client, err := adapterClient(config)
	if err != nil {
		return "", err
	}
	version, err := client.UploadAdapter(ctx, id, path, progress)
	if err != nil {
		return "", fmt.Errorf("upload adapter: %w", err)
	}
	return version, nil
}

// DeleteAdapter removes every version of id from the deployment, or only
// version when it is non-empty.
func (s *Service) DeleteAdapter(ctx context.Context, config Config, id, version string) error {
	client, err := adapterClient(config)
	if err != nil {
		return err
	}
	if err := client.DeleteAdapter(ctx, id, version); err != nil {
		return fmt.Errorf("delete adapter: %w", err)
	}
	return nil
}

func adapterClient(config Config) (*rwkvlightning.Client, error) {
	if !SupportsAdapter(config.Provider) {
		return nil, fmt.Errorf("MiSS adapters require the %s provider", ProviderRWKVLightningCUDA)
	}
	return stateClient(config)
}

func remoteAdapter(info rwkvlightning.AdapterInfo) RemoteAdapter {
	return RemoteAdapter{
		ID: info.ID, Version: info.Version,
		Rank: info.Manifest.Rank, Alpha: info.Manifest.Alpha, Scale: info.Manifest.Scale,
		BaseFingerprint: info.Manifest.BaseFingerprint, DType: info.Manifest.DType,
	}
}
