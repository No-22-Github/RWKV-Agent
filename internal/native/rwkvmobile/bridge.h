#ifndef RWKV_AGENT_GO_BRIDGE_H
#define RWKV_AGENT_GO_BRIDGE_H

#include <stdint.h>
#include "../../../native/rwkv_agent_runtime/rwkv_agent_runtime.h"

int rwa_go_stream_bridge(const rwa_stream_event *event, void *user_data);
int rwa_go_progress_bridge(uint64_t completed, uint64_t total, void *user_data);
int rwa_go_writer_bridge(const void *data, size_t size, void *user_data);
int rwa_go_reader_bridge(void *data, size_t capacity, size_t *out_size, void *user_data);

#endif
