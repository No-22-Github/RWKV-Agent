//go:build darwin && arm64 && cgo && mlx

package mlx

/*
#cgo CFLAGS: -I${SRCDIR}/../../../third_party/rwkv-mobile/src
#cgo LDFLAGS: -L${SRCDIR}/../../../build/native/rwkv-mobile -lrwkv_mobile
#include <stdlib.h>
#include "bridge.h"
*/
import "C"

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"unsafe"
)

type nativeRuntime struct {
	mu      sync.Mutex
	handle  C.rwkvmobile_runtime_t
	modelID C.int
	closed  bool
}

var generationState struct {
	sync.Mutex
	write func(string) error
	err   error
}

// rwkv-mobile's generation callback has no user-data pointer. Serialize native
// generations so the process-global callback always targets the correct writer.
var generationMu sync.Mutex

//export goRWKVGenerationCallback
func goRWKVGenerationCallback(message *C.char, code C.int, next *C.char) {
	_ = message
	if code == 0 || next == nil {
		return
	}
	text := C.GoString(next)
	if text == "" {
		return
	}

	generationState.Lock()
	defer generationState.Unlock()
	if generationState.err == nil && generationState.write != nil {
		generationState.err = generationState.write(text)
	}
}

func platformAvailable() bool {
	return true
}

func platformOpen(modelPath, tokenizerPath string) (runtimeImpl, error) {
	if err := validateModel(modelPath, tokenizerPath); err != nil {
		return nil, err
	}

	handle := C.rwkvmobile_runtime_init()
	if handle == nil {
		return nil, errors.New("rwkv-mobile runtime initialization failed")
	}

	modelCString := C.CString(modelPath)
	tokenizerCString := C.CString(tokenizerPath)
	backendCString := C.CString("mlx")
	defer C.free(unsafe.Pointer(modelCString))
	defer C.free(unsafe.Pointer(tokenizerCString))
	defer C.free(unsafe.Pointer(backendCString))

	modelID := C.rwkvmobile_runtime_load_model(handle, modelCString, backendCString, tokenizerCString)
	if modelID < 0 {
		C.rwkvmobile_runtime_release(handle)
		return nil, fmt.Errorf("rwkv-mobile failed to load the MLX model (code %d)", int(modelID))
	}

	return &nativeRuntime{handle: handle, modelID: modelID}, nil
}

func validateModel(modelPath, tokenizerPath string) error {
	info, err := os.Stat(modelPath)
	if err != nil {
		return fmt.Errorf("model directory: %w", err)
	}
	if !info.IsDir() {
		return fmt.Errorf("model path %q is not a directory", modelPath)
	}
	if _, err := os.Stat(filepath.Join(modelPath, "config.json")); err != nil {
		return fmt.Errorf("model config: %w", err)
	}
	weights, err := filepath.Glob(filepath.Join(modelPath, "*.safetensors"))
	if err != nil || len(weights) == 0 {
		return fmt.Errorf("model directory %q contains no safetensors weights", modelPath)
	}
	if _, err := os.Stat(tokenizerPath); err != nil {
		return fmt.Errorf("tokenizer: %w", err)
	}
	return nil
}

func (r *nativeRuntime) generate(ctx context.Context, prompt string, options GenerateOptions, write func(string) error) error {
	if prompt == "" {
		return errors.New("prompt must not be empty")
	}
	if options.MaxTokens <= 0 || options.Temperature <= 0 || options.TopK <= 0 || options.TopP <= 0 || options.TopP > 1 {
		return errors.New("invalid generation options")
	}
	if write == nil {
		return errors.New("stream writer must not be nil")
	}

	generationMu.Lock()
	defer generationMu.Unlock()

	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return errors.New("MLX runtime is closed")
	}

	params := C.struct_sampler_params{
		temperature: C.float(options.Temperature),
		top_k:       C.int(options.TopK),
		top_p:       C.float(options.TopP),
	}
	C.rwkvmobile_runtime_set_sampler_params(r.handle, r.modelID, params)

	generationState.Lock()
	generationState.write = write
	generationState.err = nil
	generationState.Unlock()
	defer func() {
		generationState.Lock()
		generationState.write = nil
		generationState.err = nil
		generationState.Unlock()
	}()

	promptCString := C.CString(prompt)
	defer C.free(unsafe.Pointer(promptCString))

	finished := make(chan struct{})
	go func() {
		select {
		case <-ctx.Done():
			C.rwkvmobile_runtime_stop_generation(r.handle, r.modelID)
		case <-finished:
		}
	}()

	result := C.rwkv_agent_generate(
		r.handle,
		r.modelID,
		promptCString,
		C.int(options.MaxTokens),
		0,
		0,
	)
	close(finished)

	generationState.Lock()
	writeErr := generationState.err
	generationState.Unlock()
	if writeErr != nil {
		return writeErr
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	if result != 0 {
		return fmt.Errorf("rwkv-mobile generation failed (code %d)", int(result))
	}
	return nil
}

func (r *nativeRuntime) clearState() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return errors.New("MLX runtime is closed")
	}
	if result := C.rwkvmobile_runtime_clear_state(r.handle, r.modelID); result != 0 {
		return fmt.Errorf("rwkv-mobile state reset failed (code %d)", int(result))
	}
	return nil
}

func (r *nativeRuntime) stats() Stats {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return Stats{}
	}
	return Stats{
		PrefillTokensPerSecond: float64(C.rwkvmobile_runtime_get_avg_prefill_speed(r.handle, r.modelID)),
		DecodeTokensPerSecond:  float64(C.rwkvmobile_runtime_get_avg_decode_speed(r.handle, r.modelID)),
	}
}

func (r *nativeRuntime) close() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return nil
	}
	r.closed = true

	releaseModelResult := C.rwkvmobile_runtime_release_model(r.handle, r.modelID)
	releaseRuntimeResult := C.rwkvmobile_runtime_release(r.handle)
	r.handle = nil

	if releaseModelResult != 0 {
		return fmt.Errorf("rwkv-mobile model release failed (code %d)", int(releaseModelResult))
	}
	if releaseRuntimeResult != 0 {
		return fmt.Errorf("rwkv-mobile runtime release failed (code %d)", int(releaseRuntimeResult))
	}
	return nil
}
