#include "rwkv_pth_model.h"

#include "mlx_pth_ffi.h"
#include "rwkv7_schema.h"

#include <cstdint>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <vector>

namespace {

uint16_t float_to_bf16(float value) {
    uint32_t bits = 0;
    std::memcpy(&bits, &value, sizeof(bits));
    const uint32_t exponent = bits & 0x7f800000u;
    const uint32_t mantissa = bits & 0x007fffffu;
    if (exponent == 0x7f800000u && mantissa != 0) {
        return static_cast<uint16_t>((bits >> 16) | 0x0040u);
    }
    const uint32_t round = 0x7fffu + ((bits >> 16) & 1u);
    return static_cast<uint16_t>((bits + round) >> 16);
}

class PthTensorProvider {
public:
    PthTensorProvider(const std::string &path, const std::string &index_path) {
        std::vector<rwkvmobile::PthTensorInfo> source_tensors;
        if (rwkvagent::read_rwkv7_index(
                index_path, path, schema_, source_tensors)) {
            pth_ = std::make_unique<rwkvmobile::PthFile>(path, source_tensors);
            return;
        }
        pth_ = std::make_unique<rwkvmobile::PthFile>(path);
        schema_ = rwkvagent::inspect_rwkv7_pth(*pth_);
        rwkvagent::write_rwkv7_index(index_path, path, schema_);
    }

    const rwkvagent::RWKV7Schema &schema() const { return schema_; }

    static int provide(
        void *user_data,
        int32_t tensor_index,
        const char **out_name,
        const void **out_data,
        size_t *out_byte_count,
        const int32_t **out_shape,
        int32_t *out_rank,
        int32_t *out_dtype,
        int32_t *out_transform) {
        if (!user_data) return -1;
        return static_cast<PthTensorProvider *>(user_data)->tensor(
            tensor_index,
            out_name,
            out_data,
            out_byte_count,
            out_shape,
            out_rank,
            out_dtype,
            out_transform);
    }

private:
    int tensor(
        int32_t tensor_index,
        const char **out_name,
        const void **out_data,
        size_t *out_byte_count,
        const int32_t **out_shape,
        int32_t *out_rank,
        int32_t *out_dtype,
        int32_t *out_transform) {
        if (tensor_index < 0 ||
            static_cast<size_t>(tensor_index) >= schema_.tensors.size() ||
            !out_name || !out_data || !out_byte_count || !out_shape ||
            !out_rank || !out_dtype || !out_transform) {
            return -1;
        }
        const auto &spec = schema_.tensors[static_cast<size_t>(tensor_index)];
        shape_.clear();
        const auto &shape =
            spec.transform == rwkvagent::TensorTransform::Transpose2D
                ? spec.source_shape
                : spec.target_shape;
        if (shape.size() > static_cast<size_t>(std::numeric_limits<int32_t>::max())) {
            return -1;
        }
        for (int64_t dim : shape) {
            if (dim < 0 || dim > std::numeric_limits<int32_t>::max()) {
                return -1;
            }
            shape_.push_back(static_cast<int32_t>(dim));
        }

        *out_name = spec.target_name.c_str();
        *out_shape = shape_.data();
        *out_rank = static_cast<int32_t>(shape_.size());
        *out_transform =
            spec.transform == rwkvagent::TensorTransform::Transpose2D
                ? MLX_PTH_TRANSPOSE_2D
                : MLX_PTH_IDENTITY;

        rwkvmobile::PthTensorView view;
        if (pth_->read_tensor_view(spec.source_name, view)) {
            *out_data = view.data;
            *out_byte_count = view.byte_count;
            switch (spec.dtype) {
                case rwkvmobile::PthDType::Float32:
                    *out_dtype = MLX_PTH_F32;
                    break;
                case rwkvmobile::PthDType::Float16:
                    *out_dtype = MLX_PTH_F16;
                    break;
                case rwkvmobile::PthDType::BFloat16:
                    *out_dtype = MLX_PTH_BF16;
                    break;
            }
            return 0;
        }

        switch (spec.dtype) {
            case rwkvmobile::PthDType::Float32:
                float32_ = pth_->read_tensor_float32(spec.source_name);
                *out_data = float32_.data();
                *out_byte_count = float32_.size() * sizeof(float);
                *out_dtype = MLX_PTH_F32;
                break;
            case rwkvmobile::PthDType::Float16:
                float16_ = pth_->read_tensor_float16(spec.source_name);
                *out_data = float16_.data();
                *out_byte_count = float16_.size() * sizeof(uint16_t);
                *out_dtype = MLX_PTH_F16;
                break;
            case rwkvmobile::PthDType::BFloat16:
                float32_ = pth_->read_tensor_float32(spec.source_name);
                bfloat16_.resize(float32_.size());
                for (size_t i = 0; i < float32_.size(); ++i) {
                    bfloat16_[i] = float_to_bf16(float32_[i]);
                }
                *out_data = bfloat16_.data();
                *out_byte_count = bfloat16_.size() * sizeof(uint16_t);
                *out_dtype = MLX_PTH_BF16;
                break;
        }
        return 0;
    }

    std::unique_ptr<rwkvmobile::PthFile> pth_;
    rwkvagent::RWKV7Schema schema_;
    std::vector<int32_t> shape_;
    std::vector<float> float32_;
    std::vector<half_float::half> float16_;
    std::vector<uint16_t> bfloat16_;
};

} // namespace

void *rwkv_agent_load_pth_model(
    const std::string &pth_path,
    const std::string &index_path,
    std::string &error) {
    try {
        PthTensorProvider provider(pth_path, index_path);
        const std::string config = rwkvagent::rwkv7_config_json(provider.schema().config);
        void *model = mlx_model_load_pth(
            config.c_str(),
            static_cast<int32_t>(provider.schema().tensors.size()),
            &PthTensorProvider::provide,
            &provider);
        if (!model) {
            error = "MLX rejected direct PTH weights";
        }
        return model;
    } catch (const std::exception &exception) {
        error = exception.what();
        return nullptr;
    } catch (...) {
        error = "unknown direct PTH load failure";
        return nullptr;
    }
}
