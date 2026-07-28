#ifndef RWKV_AGENT_RUNTIME_H
#define RWKV_AGENT_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define RWA_API __declspec(dllexport)
#else
#define RWA_API __attribute__((visibility("default")))
#endif

#define RWA_ABI_VERSION 1u
#define RWA_CAP_NATIVE_STATE (1ull << 0)
#define RWA_CAP_CONTINUOUS_BATCH (1ull << 1)
#define RWA_CAP_EXACT_TOKENS (1ull << 2)
#define RWA_CAP_CANCELLATION (1ull << 3)

typedef enum rwa_status {
    RWA_OK = 0,
    RWA_INVALID_ARGUMENT = 1,
    RWA_UNAVAILABLE = 2,
    RWA_UNSUPPORTED = 3,
    RWA_BUSY = 4,
    RWA_CANCELLED = 5,
    RWA_INCOMPATIBLE_STATE = 6,
    RWA_CORRUPT_STATE = 7,
    RWA_BACKEND_FAILURE = 8,
    RWA_CLOSED = 9,
    RWA_CAPACITY = 10
} rwa_status;

typedef enum rwa_session_status {
    RWA_SESSION_CLEAN = 0,
    RWA_SESSION_GENERATING = 1,
    RWA_SESSION_DIRTY = 2,
    RWA_SESSION_REBUILDING = 3,
    RWA_SESSION_CLOSED = 4
} rwa_session_status;

typedef enum rwa_finish_reason {
    RWA_FINISH_STOP = 0,
    RWA_FINISH_LENGTH = 1,
    RWA_FINISH_CANCELLED = 2,
    RWA_FINISH_ERROR = 3
} rwa_finish_reason;

typedef enum rwa_stream_event_kind {
    RWA_STREAM_TOKEN = 1,
    RWA_STREAM_FINISH = 2,
    RWA_STREAM_WARNING = 3
} rwa_stream_event_kind;

typedef struct rwa_runtime rwa_runtime;
typedef struct rwa_model rwa_model;
typedef struct rwa_session rwa_session;

typedef struct rwa_runtime_options {
    uint32_t struct_size;
    uint32_t max_active_batch;
    uint32_t queue_capacity;
} rwa_runtime_options;

typedef struct rwa_model_options {
    uint32_t struct_size;
    const char *model_path;
    const char *tokenizer_path;
    const char *provider;
} rwa_model_options;

typedef struct rwa_session_options {
    uint32_t struct_size;
} rwa_session_options;

typedef struct rwa_capabilities {
    uint32_t struct_size;
    uint64_t flags;
    uint32_t max_state_slots;
    uint32_t available_state_slots;
    uint32_t max_active_batch;
    uint32_t queue_capacity;
    uint32_t max_observed_batch;
} rwa_capabilities;

typedef struct rwa_generate_options {
    uint32_t struct_size;
    uint64_t request_id;
    const int32_t *input_token_ids;
    size_t input_token_count;
    uint32_t max_output_tokens;
    float temperature;
    int32_t top_k;
    float top_p;
    float presence_penalty;
    float frequency_penalty;
    float penalty_decay;
    uint64_t seed;
    uint32_t has_seed;
} rwa_generate_options;

typedef struct rwa_stream_event {
    uint32_t struct_size;
    uint32_t kind;
    uint64_t request_id;
    int32_t token_id;
    const char *text;
    size_t text_size;
} rwa_stream_event;

typedef int (*rwa_stream_callback)(const rwa_stream_event *event, void *user_data);
typedef int (*rwa_prefill_progress_callback)(
    uint64_t completed_tokens,
    uint64_t total_tokens,
    void *user_data);

typedef struct rwa_generate_result {
    uint32_t struct_size;
    uint32_t finish_reason;
    uint32_t state_clean;
    uint32_t reserved;
    uint64_t prefill_tokens;
    uint64_t decode_tokens;
    double prefill_tokens_per_second;
    double decode_tokens_per_second;
    uint64_t prefix_hash;
} rwa_generate_result;

typedef struct rwa_session_info {
    uint32_t struct_size;
    uint32_t status;
    uint64_t prefix_token_count;
    uint64_t prefix_hash;
    uint64_t active_request_id;
    const char *dirty_reason;
} rwa_session_info;

typedef int (*rwa_writer)(const void *data, size_t size, void *user_data);
typedef int (*rwa_reader)(void *data, size_t capacity, size_t *out_size, void *user_data);

typedef struct rwa_state_descriptor {
    uint32_t struct_size;
    uint32_t format_version;
    uint64_t prefix_token_count;
    uint64_t prefix_hash;
    const char *codec_id;
    uint32_t codec_version;
} rwa_state_descriptor;

RWA_API uint32_t rwa_abi_version(void);
RWA_API const char *rwa_status_string(rwa_status status);

RWA_API rwa_status rwa_runtime_create(
    const rwa_runtime_options *options,
    rwa_runtime **out_runtime);
RWA_API rwa_status rwa_runtime_destroy(rwa_runtime *runtime);
RWA_API const char *rwa_runtime_last_error(const rwa_runtime *runtime);

RWA_API rwa_status rwa_model_load(
    rwa_runtime *runtime,
    const rwa_model_options *options,
    rwa_model **out_model);
RWA_API rwa_status rwa_model_destroy(rwa_model *model);
RWA_API const char *rwa_model_last_error(const rwa_model *model);
RWA_API rwa_status rwa_model_capabilities(
    const rwa_model *model,
    rwa_capabilities *out_capabilities);
RWA_API rwa_status rwa_model_encode(
    rwa_model *model,
    const char *utf8,
    size_t utf8_size,
    int32_t **out_tokens,
    size_t *out_token_count);
RWA_API void rwa_token_buffer_free(int32_t *tokens);

RWA_API rwa_status rwa_session_create(
    rwa_model *model,
    const rwa_session_options *options,
    rwa_session **out_session);
RWA_API rwa_status rwa_session_destroy(rwa_session *session);
RWA_API const char *rwa_session_last_error(const rwa_session *session);
RWA_API rwa_status rwa_session_info_get(
    const rwa_session *session,
    rwa_session_info *out_info);
RWA_API rwa_status rwa_session_reset(rwa_session *session);
RWA_API rwa_status rwa_session_sync_prefix(
    rwa_session *session,
    const int32_t *token_ids,
    size_t token_count,
    rwa_prefill_progress_callback callback,
    void *user_data);
RWA_API rwa_status rwa_session_generate(
    rwa_session *session,
    const rwa_generate_options *options,
    rwa_stream_callback callback,
    void *user_data,
    rwa_generate_result *out_result);
RWA_API rwa_status rwa_session_cancel(
    rwa_session *session,
    uint64_t request_id);
RWA_API rwa_status rwa_session_export_state(
    rwa_session *session,
    rwa_writer writer,
    void *user_data,
    rwa_state_descriptor *out_descriptor);
RWA_API rwa_status rwa_session_import_state(
    rwa_session *session,
    rwa_reader reader,
    void *user_data,
    const rwa_state_descriptor *descriptor);

#ifdef __cplusplus
}
#endif

#endif
