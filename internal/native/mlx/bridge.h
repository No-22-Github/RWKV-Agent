#ifndef RWKV_AGENT_MLX_BRIDGE_H
#define RWKV_AGENT_MLX_BRIDGE_H

#include "c_api.h"

int rwkv_agent_generate(
    rwkvmobile_runtime_t runtime,
    int model_id,
    const char *prompt,
    int max_tokens,
    int stop_code,
    int disable_cache
);

#endif
