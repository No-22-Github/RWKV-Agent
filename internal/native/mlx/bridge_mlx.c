//go:build darwin && arm64 && cgo && mlx

#include "bridge.h"

extern void goRWKVGenerationCallback(char *message, int code, char *next);

static void rwkv_agent_generation_callback(const char *message, const int code, const char *next) {
    goRWKVGenerationCallback((char *)message, code, (char *)next);
}

int rwkv_agent_generate(
    rwkvmobile_runtime_t runtime,
    int model_id,
    const char *prompt,
    int max_tokens,
    int stop_code,
    int disable_cache
) {
    return rwkvmobile_runtime_gen_completion(
        runtime,
        model_id,
        prompt,
        max_tokens,
        stop_code,
        rwkv_agent_generation_callback,
        disable_cache
    );
}
