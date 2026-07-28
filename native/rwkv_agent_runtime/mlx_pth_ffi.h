#ifndef RWKV_AGENT_MLX_PTH_FFI_H
#define RWKV_AGENT_MLX_PTH_FFI_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum mlx_pth_dtype {
    MLX_PTH_F32 = 0,
    MLX_PTH_F16 = 1,
    MLX_PTH_BF16 = 2,
};

enum mlx_pth_transform {
    MLX_PTH_IDENTITY = 0,
    MLX_PTH_TRANSPOSE_2D = 1,
};

typedef int (*mlx_pth_tensor_provider)(
    void *user_data,
    int32_t tensor_index,
    const char **out_name,
    const void **out_data,
    size_t *out_byte_count,
    const int32_t **out_shape,
    int32_t *out_rank,
    int32_t *out_dtype,
    int32_t *out_transform);

void *mlx_model_load_pth(
    const char *config_json,
    int32_t tensor_count,
    mlx_pth_tensor_provider provider,
    void *user_data);

#ifdef __cplusplus
}
#endif

#endif
