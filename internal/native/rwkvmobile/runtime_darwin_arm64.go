//go:build darwin && arm64 && cgo && mlx

package rwkvmobile

/*
#cgo CFLAGS: -I${SRCDIR}/../../../native/rwkv_agent_runtime
#cgo LDFLAGS: -L${SRCDIR}/../../../build/native/agent-runtime -lrwkv_agent_runtime
#include <stdlib.h>
#include "bridge.h"
*/
import "C"

import (
	"context"
	"errors"
	"io"
	"runtime/cgo"
	"sync"
	"unsafe"
)

type nativeRuntime struct {
	mu     sync.Mutex
	handle *C.rwa_runtime
	closed bool
}

type nativeModel struct {
	mu      sync.Mutex
	runtime *nativeRuntime
	handle  *C.rwa_model
	closed  bool
}

type nativeSession struct {
	mu     sync.Mutex
	model  *nativeModel
	handle *C.rwa_session
	closed bool
}

type callbackState struct {
	callback func(StreamEvent) error
	progress func(int, int) error
	writer   io.Writer
	reader   io.Reader
	mu       sync.Mutex
	err      error
}

func (s *callbackState) setError(err error) {
	if err == nil {
		return
	}
	s.mu.Lock()
	if s.err == nil {
		s.err = err
	}
	s.mu.Unlock()
}

func (s *callbackState) callbackError() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.err
}

//export goRWAStreamCallback
func goRWAStreamCallback(event *C.rwa_stream_event, handle C.uintptr_t) C.int {
	state := cgo.Handle(handle).Value().(*callbackState)
	if event == nil || state.callback == nil {
		return 1
	}
	text := ""
	if event.text != nil && event.text_size > 0 {
		text = C.GoStringN(event.text, C.int(event.text_size))
	}
	err := state.callback(StreamEvent{
		RequestID: uint64(event.request_id),
		TokenID:   int32(event.token_id),
		Text:      text,
		Finish:    event.kind == C.RWA_STREAM_FINISH,
		Warning:   event.kind == C.RWA_STREAM_WARNING,
	})
	if err != nil {
		state.setError(err)
		return 1
	}
	return 0
}

//export goRWAPrefillProgress
func goRWAPrefillProgress(completed C.uint64_t, total C.uint64_t, handle C.uintptr_t) C.int {
	state := cgo.Handle(handle).Value().(*callbackState)
	if state.progress == nil {
		return 0
	}
	if err := state.progress(int(completed), int(total)); err != nil {
		state.setError(err)
		return 1
	}
	return 0
}

//export goRWAWriter
func goRWAWriter(data unsafe.Pointer, size C.size_t, handle C.uintptr_t) C.int {
	state := cgo.Handle(handle).Value().(*callbackState)
	if state.writer == nil || size > C.size_t(maxInt()) {
		return 1
	}
	buffer := unsafe.Slice((*byte)(data), int(size))
	written, err := state.writer.Write(buffer)
	if err == nil && written != len(buffer) {
		err = io.ErrShortWrite
	}
	if err != nil {
		state.setError(err)
		return 1
	}
	return 0
}

//export goRWAReader
func goRWAReader(data unsafe.Pointer, capacity C.size_t, outSize *C.size_t, handle C.uintptr_t) C.int {
	state := cgo.Handle(handle).Value().(*callbackState)
	if state.reader == nil || outSize == nil || capacity > C.size_t(maxInt()) {
		return 1
	}
	buffer := unsafe.Slice((*byte)(data), int(capacity))
	read, err := state.reader.Read(buffer)
	*outSize = C.size_t(read)
	if errors.Is(err, io.EOF) {
		return 0
	}
	if err != nil {
		state.setError(err)
		return 1
	}
	return 0
}

func maxInt() int {
	return int(^uint(0) >> 1)
}

func platformAvailable() bool {
	return C.rwa_abi_version() == C.RWA_ABI_VERSION
}

func platformOpen(options Options) (runtimeImpl, error) {
	nativeOptions := C.rwa_runtime_options{
		struct_size:      C.uint32_t(C.sizeof_rwa_runtime_options),
		max_active_batch: C.uint32_t(options.MaxActiveBatch),
		queue_capacity:   C.uint32_t(options.QueueCapacity),
	}
	var handle *C.rwa_runtime
	status := C.rwa_runtime_create(&nativeOptions, &handle)
	if status != C.RWA_OK {
		return nil, statusError(status, "")
	}
	return &nativeRuntime{handle: handle}, nil
}

func (r *nativeRuntime) loadModel(options ModelOptions) (modelImpl, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return nil, statusError(C.RWA_CLOSED, "native runtime is closed")
	}
	modelPath := C.CString(options.Path)
	tokenizerPath := C.CString(options.TokenizerPath)
	provider := C.CString(options.Provider)
	defer C.free(unsafe.Pointer(modelPath))
	defer C.free(unsafe.Pointer(tokenizerPath))
	defer C.free(unsafe.Pointer(provider))
	nativeOptions := C.rwa_model_options{
		struct_size:    C.uint32_t(C.sizeof_rwa_model_options),
		model_path:     modelPath,
		tokenizer_path: tokenizerPath,
		provider:       provider,
	}
	var handle *C.rwa_model
	status := C.rwa_model_load(r.handle, &nativeOptions, &handle)
	if status != C.RWA_OK {
		return nil, statusError(status, C.GoString(C.rwa_runtime_last_error(r.handle)))
	}
	return &nativeModel{runtime: r, handle: handle}, nil
}

func (r *nativeRuntime) close() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.closed {
		return nil
	}
	r.closed = true
	status := C.rwa_runtime_destroy(r.handle)
	r.handle = nil
	return statusErrorOrNil(status, "")
}

func (m *nativeModel) encode(text string) ([]int32, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return nil, statusError(C.RWA_CLOSED, "native model is closed")
	}
	input := C.CString(text)
	defer C.free(unsafe.Pointer(input))
	var tokens *C.int32_t
	var count C.size_t
	status := C.rwa_model_encode(
		m.handle, input, C.size_t(len(text)), &tokens, &count)
	if status != C.RWA_OK {
		return nil, statusError(status, C.GoString(C.rwa_model_last_error(m.handle)))
	}
	defer C.rwa_token_buffer_free(tokens)
	if count == 0 {
		return nil, nil
	}
	native := unsafe.Slice(tokens, int(count))
	result := make([]int32, len(native))
	for i, token := range native {
		result[i] = int32(token)
	}
	return result, nil
}

func (m *nativeModel) capabilities() (Capabilities, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return Capabilities{}, statusError(C.RWA_CLOSED, "native model is closed")
	}
	value := C.rwa_capabilities{struct_size: C.uint32_t(C.sizeof_rwa_capabilities)}
	status := C.rwa_model_capabilities(m.handle, &value)
	if status != C.RWA_OK {
		return Capabilities{}, statusError(status, C.GoString(C.rwa_model_last_error(m.handle)))
	}
	flags := uint64(value.flags)
	return Capabilities{
		NativeState:      flags&uint64(C.RWA_CAP_NATIVE_STATE) != 0,
		ContinuousBatch:  flags&uint64(C.RWA_CAP_CONTINUOUS_BATCH) != 0,
		ExactTokens:      flags&uint64(C.RWA_CAP_EXACT_TOKENS) != 0,
		Cancellation:     flags&uint64(C.RWA_CAP_CANCELLATION) != 0,
		MaxStateSlots:    int(value.max_state_slots),
		AvailableSlots:   int(value.available_state_slots),
		MaxActiveBatch:   int(value.max_active_batch),
		QueueCapacity:    int(value.queue_capacity),
		MaxObservedBatch: int(value.max_observed_batch),
	}, nil
}

func (m *nativeModel) newSession() (sessionImpl, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return nil, statusError(C.RWA_CLOSED, "native model is closed")
	}
	options := C.rwa_session_options{struct_size: C.uint32_t(C.sizeof_rwa_session_options)}
	var handle *C.rwa_session
	status := C.rwa_session_create(m.handle, &options, &handle)
	if status != C.RWA_OK {
		return nil, statusError(status, C.GoString(C.rwa_model_last_error(m.handle)))
	}
	return &nativeSession{model: m, handle: handle}, nil
}

func (m *nativeModel) close() error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return nil
	}
	m.closed = true
	status := C.rwa_model_destroy(m.handle)
	m.handle = nil
	return statusErrorOrNil(status, "")
}

func (s *nativeSession) syncPrefix(
	ctx context.Context,
	tokens []int32,
	progress func(int, int) error,
) error {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return statusError(C.RWA_CLOSED, "native session is closed")
	}
	handle := s.handle
	s.mu.Unlock()

	state := &callbackState{progress: func(completed, total int) error {
		if err := ctx.Err(); err != nil {
			return err
		}
		if progress != nil {
			return progress(completed, total)
		}
		return nil
	}}
	callbackHandle := cgo.NewHandle(state)
	defer callbackHandle.Delete()
	var tokenPtr *C.int32_t
	if len(tokens) > 0 {
		tokenPtr = (*C.int32_t)(unsafe.Pointer(&tokens[0]))
	}
	done := make(chan struct{})
	go func() {
		select {
		case <-ctx.Done():
			info, err := s.info()
			if err == nil && info.ActiveRequestID != 0 {
				_ = s.cancel(info.ActiveRequestID)
			}
		case <-done:
		}
	}()
	status := C.rwa_session_sync_prefix(
		handle,
		tokenPtr,
		C.size_t(len(tokens)),
		(C.rwa_prefill_progress_callback)(C.rwa_go_progress_bridge),
		unsafe.Pointer(uintptr(callbackHandle)),
	)
	close(done)
	if err := state.callbackError(); err != nil {
		return err
	}
	if err := ctx.Err(); err != nil {
		return err
	}
	return statusErrorOrNil(status, C.GoString(C.rwa_session_last_error(handle)))
}

func (s *nativeSession) generate(
	ctx context.Context,
	options GenerateOptions,
	callback func(StreamEvent) error,
) (GenerateResult, error) {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return GenerateResult{}, statusError(C.RWA_CLOSED, "native session is closed")
	}
	handle := s.handle
	s.mu.Unlock()
	if len(options.InputTokens) == 0 || callback == nil {
		return GenerateResult{}, statusError(C.RWA_INVALID_ARGUMENT, "tokens and callback are required")
	}
	tokenBytes := C.size_t(len(options.InputTokens)) * C.size_t(unsafe.Sizeof(C.int32_t(0)))
	tokenBuffer := C.malloc(tokenBytes)
	if tokenBuffer == nil {
		return GenerateResult{}, statusError(C.RWA_BACKEND_FAILURE, "allocate native token buffer")
	}
	defer C.free(tokenBuffer)
	nativeTokens := unsafe.Slice((*C.int32_t)(tokenBuffer), len(options.InputTokens))
	for index, token := range options.InputTokens {
		nativeTokens[index] = C.int32_t(token)
	}

	nativeOptions := C.rwa_generate_options{
		struct_size:       C.uint32_t(C.sizeof_rwa_generate_options),
		request_id:        C.uint64_t(options.RequestID),
		input_token_ids:   (*C.int32_t)(tokenBuffer),
		input_token_count: C.size_t(len(options.InputTokens)),
		max_output_tokens: C.uint32_t(options.MaxOutputTokens),
		temperature:       C.float(options.Temperature),
		top_k:             C.int32_t(options.TopK),
		top_p:             C.float(options.TopP),
		presence_penalty:  C.float(options.PresencePenalty),
		frequency_penalty: C.float(options.FrequencyPenalty),
		penalty_decay:     C.float(options.PenaltyDecay),
	}
	if options.Seed != nil {
		nativeOptions.seed = C.uint64_t(*options.Seed)
		nativeOptions.has_seed = 1
	}
	nativeResult := C.rwa_generate_result{
		struct_size: C.uint32_t(C.sizeof_rwa_generate_result),
	}
	state := &callbackState{callback: callback}
	callbackHandle := cgo.NewHandle(state)
	defer callbackHandle.Delete()
	done := make(chan struct{})
	go func() {
		select {
		case <-ctx.Done():
			_ = s.cancel(options.RequestID)
		case <-done:
		}
	}()
	status := C.rwa_session_generate(
		handle,
		&nativeOptions,
		(C.rwa_stream_callback)(C.rwa_go_stream_bridge),
		unsafe.Pointer(uintptr(callbackHandle)),
		&nativeResult,
	)
	close(done)
	result := GenerateResult{
		FinishReason:           finishReason(nativeResult.finish_reason),
		StateClean:             nativeResult.state_clean != 0,
		PrefillTokens:          int(nativeResult.prefill_tokens),
		DecodeTokens:           int(nativeResult.decode_tokens),
		PrefillTokensPerSecond: float64(nativeResult.prefill_tokens_per_second),
		DecodeTokensPerSecond:  float64(nativeResult.decode_tokens_per_second),
		PrefixHash:             uint64(nativeResult.prefix_hash),
	}
	if err := state.callbackError(); err != nil {
		return result, err
	}
	if err := ctx.Err(); err != nil {
		return result, err
	}
	return result, statusErrorOrNil(status, C.GoString(C.rwa_session_last_error(handle)))
}

func (s *nativeSession) cancel(requestID uint64) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return statusError(C.RWA_CLOSED, "native session is closed")
	}
	status := C.rwa_session_cancel(s.handle, C.uint64_t(requestID))
	return statusErrorOrNil(status, C.GoString(C.rwa_session_last_error(s.handle)))
}

func (s *nativeSession) reset() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return statusError(C.RWA_CLOSED, "native session is closed")
	}
	status := C.rwa_session_reset(s.handle)
	return statusErrorOrNil(status, C.GoString(C.rwa_session_last_error(s.handle)))
}

func (s *nativeSession) info() (SessionInfo, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return SessionInfo{Status: "closed"}, statusError(C.RWA_CLOSED, "native session is closed")
	}
	value := C.rwa_session_info{struct_size: C.uint32_t(C.sizeof_rwa_session_info)}
	status := C.rwa_session_info_get(s.handle, &value)
	if status != C.RWA_OK {
		return SessionInfo{}, statusError(status, C.GoString(C.rwa_session_last_error(s.handle)))
	}
	dirtyReason := ""
	if value.dirty_reason != nil {
		dirtyReason = C.GoString(value.dirty_reason)
	}
	return SessionInfo{
		Status:           sessionStatus(value.status),
		PrefixTokenCount: int(value.prefix_token_count),
		PrefixHash:       uint64(value.prefix_hash),
		ActiveRequestID:  uint64(value.active_request_id),
		DirtyReason:      dirtyReason,
	}, nil
}

func (s *nativeSession) exportState(writer io.Writer) (StateDescriptor, error) {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return StateDescriptor{}, statusError(C.RWA_CLOSED, "native session is closed")
	}
	handle := s.handle
	s.mu.Unlock()
	state := &callbackState{writer: writer}
	callbackHandle := cgo.NewHandle(state)
	defer callbackHandle.Delete()
	value := C.rwa_state_descriptor{
		struct_size: C.uint32_t(C.sizeof_rwa_state_descriptor),
	}
	status := C.rwa_session_export_state(
		handle,
		(C.rwa_writer)(C.rwa_go_writer_bridge),
		unsafe.Pointer(uintptr(callbackHandle)),
		&value,
	)
	if err := state.callbackError(); err != nil {
		return StateDescriptor{}, err
	}
	if status != C.RWA_OK {
		return StateDescriptor{}, statusError(status, C.GoString(C.rwa_session_last_error(handle)))
	}
	return stateDescriptorFromC(value), nil
}

func (s *nativeSession) importState(reader io.Reader, descriptor StateDescriptor) error {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return statusError(C.RWA_CLOSED, "native session is closed")
	}
	handle := s.handle
	s.mu.Unlock()
	codec := C.CString(descriptor.CodecID)
	defer C.free(unsafe.Pointer(codec))
	value := C.rwa_state_descriptor{
		struct_size:        C.uint32_t(C.sizeof_rwa_state_descriptor),
		format_version:     C.uint32_t(descriptor.FormatVersion),
		prefix_token_count: C.uint64_t(descriptor.PrefixTokenCount),
		prefix_hash:        C.uint64_t(descriptor.PrefixHash),
		codec_id:           codec,
		codec_version:      C.uint32_t(descriptor.CodecVersion),
	}
	state := &callbackState{reader: reader}
	callbackHandle := cgo.NewHandle(state)
	defer callbackHandle.Delete()
	status := C.rwa_session_import_state(
		handle,
		(C.rwa_reader)(C.rwa_go_reader_bridge),
		unsafe.Pointer(uintptr(callbackHandle)),
		&value,
	)
	if err := state.callbackError(); err != nil {
		return err
	}
	return statusErrorOrNil(status, C.GoString(C.rwa_session_last_error(handle)))
}

func (s *nativeSession) close() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return nil
	}
	s.closed = true
	status := C.rwa_session_destroy(s.handle)
	s.handle = nil
	return statusErrorOrNil(status, "")
}

func statusErrorOrNil(status C.rwa_status, message string) error {
	if status == C.RWA_OK {
		return nil
	}
	return statusError(status, message)
}

func statusError(status C.rwa_status, message string) error {
	if message == "" {
		message = C.GoString(C.rwa_status_string(status))
	}
	return &Error{Status: Status(status), Message: message}
}

func finishReason(reason C.uint32_t) string {
	switch reason {
	case C.RWA_FINISH_STOP:
		return "stop"
	case C.RWA_FINISH_LENGTH:
		return "length"
	case C.RWA_FINISH_CANCELLED:
		return "cancelled"
	default:
		return "error"
	}
}

func sessionStatus(status C.uint32_t) string {
	switch status {
	case C.RWA_SESSION_CLEAN:
		return "clean"
	case C.RWA_SESSION_GENERATING:
		return "generating"
	case C.RWA_SESSION_DIRTY:
		return "dirty"
	case C.RWA_SESSION_REBUILDING:
		return "rebuilding"
	default:
		return "closed"
	}
}

func stateDescriptorFromC(value C.rwa_state_descriptor) StateDescriptor {
	codec := ""
	if value.codec_id != nil {
		codec = C.GoString(value.codec_id)
	}
	return StateDescriptor{
		FormatVersion:    int(value.format_version),
		PrefixTokenCount: int(value.prefix_token_count),
		PrefixHash:       uint64(value.prefix_hash),
		CodecID:          codec,
		CodecVersion:     int(value.codec_version),
	}
}
