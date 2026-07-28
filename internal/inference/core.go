package inference

import (
	"context"
	"errors"
	"fmt"
	"sync"
)

type Core struct {
	mu       sync.Mutex
	backends []Backend
	models   []Model
	closed   bool
}

func NewCore(backends ...Backend) (*Core, error) {
	seen := make(map[BackendID]struct{}, len(backends))
	for _, backend := range backends {
		if backend == nil {
			return nil, fmt.Errorf("%w: nil backend", ErrInvalidArgument)
		}
		id := backend.Info().ID
		if id == "" {
			return nil, fmt.Errorf("%w: backend ID is required", ErrInvalidArgument)
		}
		if _, exists := seen[id]; exists {
			return nil, fmt.Errorf("%w: duplicate backend %q", ErrInvalidArgument, id)
		}
		seen[id] = struct{}{}
	}
	return &Core{backends: append([]Backend(nil), backends...)}, nil
}

func (c *Core) Backends(ctx context.Context) ([]BackendInfo, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	if c.closed {
		return nil, opError("list backends", CodeClosed, "", ErrClosed)
	}
	infos := make([]BackendInfo, 0, len(c.backends))
	for _, backend := range c.backends {
		infos = append(infos, backend.Info())
	}
	return infos, nil
}

func (c *Core) ProbeModel(ctx context.Context, source ModelSource) (ModelInfo, error) {
	if err := validateModelSource(source); err != nil {
		return ModelInfo{}, err
	}
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return ModelInfo{}, opError("probe model", CodeClosed, "", ErrClosed)
	}
	backends := append([]Backend(nil), c.backends...)
	c.mu.Unlock()

	var probeErrors []error
	for _, backend := range backends {
		info := backend.Info()
		if !info.Available {
			continue
		}
		modelInfo, err := backend.ProbeModel(ctx, source)
		if err == nil {
			return modelInfo, nil
		}
		probeErrors = append(probeErrors, err)
	}
	if len(probeErrors) == 0 {
		return ModelInfo{}, opError("probe model", CodeUnavailable, "", ErrUnavailable)
	}
	return ModelInfo{}, errors.Join(probeErrors...)
}

func (c *Core) LoadModel(ctx context.Context, request LoadRequest, progress ProgressSink) (Model, error) {
	if err := validateModelSource(request.Source); err != nil {
		return nil, err
	}
	if request.Backend == "" {
		request.Backend = BackendAuto
	}

	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return nil, opError("load model", CodeClosed, request.Backend, ErrClosed)
	}
	backends := append([]Backend(nil), c.backends...)
	c.mu.Unlock()

	if request.Backend != BackendAuto {
		for _, backend := range backends {
			info := backend.Info()
			if info.ID != request.Backend {
				continue
			}
			if !info.Available {
				err := ErrUnavailable
				if info.UnavailableReason != "" {
					err = fmt.Errorf("%w: %s", ErrUnavailable, info.UnavailableReason)
				}
				return nil, opError("load model", CodeUnavailable, info.ID, err)
			}
			model, err := backend.LoadModel(ctx, request, progress)
			if err != nil {
				return nil, err
			}
			return c.trackModel(model, request.Backend)
		}
		return nil, opError(
			"load model",
			CodeUnavailable,
			request.Backend,
			fmt.Errorf("%w: backend %q is not registered", ErrUnavailable, request.Backend),
		)
	}

	var loadErrors []error
	for _, backend := range backends {
		info := backend.Info()
		if !info.Available {
			continue
		}
		candidate := request
		candidate.Backend = info.ID
		model, err := backend.LoadModel(ctx, candidate, progress)
		if err == nil {
			return c.trackModel(model, info.ID)
		}
		loadErrors = append(loadErrors, err)
	}
	if len(loadErrors) == 0 {
		return nil, opError("load model", CodeUnavailable, BackendAuto, ErrUnavailable)
	}
	return nil, errors.Join(loadErrors...)
}

func (c *Core) trackModel(model Model, backend BackendID) (Model, error) {
	c.mu.Lock()
	if !c.closed {
		c.models = append(c.models, model)
		c.mu.Unlock()
		return model, nil
	}
	c.mu.Unlock()
	_ = model.Close()
	return nil, opError("load model", CodeClosed, backend, ErrClosed)
}

func (c *Core) Close() error {
	if c == nil {
		return nil
	}
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return nil
	}
	c.closed = true
	models := append([]Model(nil), c.models...)
	c.models = nil
	c.mu.Unlock()

	var closeErrors []error
	for i := len(models) - 1; i >= 0; i-- {
		if err := models[i].Close(); err != nil {
			closeErrors = append(closeErrors, err)
		}
	}
	return errors.Join(closeErrors...)
}

func validateModelSource(source ModelSource) error {
	if source.Path == "" {
		return fmt.Errorf("%w: model path is required", ErrInvalidArgument)
	}
	return nil
}
