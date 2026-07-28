//go:build darwin && arm64 && cgo && mlx

#include "bridge.h"

extern int goRWAStreamCallback(const rwa_stream_event *event, uintptr_t handle);
extern int goRWAPrefillProgress(uint64_t completed, uint64_t total, uintptr_t handle);
extern int goRWAWriter(const void *data, size_t size, uintptr_t handle);
extern int goRWAReader(void *data, size_t capacity, size_t *out_size, uintptr_t handle);

int rwa_go_stream_bridge(const rwa_stream_event *event, void *user_data) {
    return goRWAStreamCallback(event, (uintptr_t)user_data);
}

int rwa_go_progress_bridge(uint64_t completed, uint64_t total, void *user_data) {
    return goRWAPrefillProgress(completed, total, (uintptr_t)user_data);
}

int rwa_go_writer_bridge(const void *data, size_t size, void *user_data) {
    return goRWAWriter(data, size, (uintptr_t)user_data);
}

int rwa_go_reader_bridge(void *data, size_t capacity, size_t *out_size, void *user_data) {
    return goRWAReader(data, capacity, out_size, (uintptr_t)user_data);
}
