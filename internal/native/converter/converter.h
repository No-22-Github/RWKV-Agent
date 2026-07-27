#ifndef RWKV_AGENT_CONVERTER_H
#define RWKV_AGENT_CONVERTER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

int rwkv_agent_convert_pth(
    const char *input_path,
    const char *output_path,
    const char *tokenizer_path,
    const char *precision,
    int overwrite,
    char *error_buffer,
    size_t error_capacity
);

#ifdef __cplusplus
}
#endif

#endif
