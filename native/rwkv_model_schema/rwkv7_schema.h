#ifndef RWKV_AGENT_RWKV7_SCHEMA_H
#define RWKV_AGENT_RWKV7_SCHEMA_H

#include "pth_loader.h"

#include <cstdint>
#include <string>
#include <vector>

namespace rwkvagent {

enum class TensorTransform {
    Identity = 0,
    Transpose2D = 1,
};

struct RWKV7Config {
    int64_t vocab_size = 0;
    int64_t hidden_size = 0;
    int64_t intermediate_size = 0;
    int64_t num_hidden_layers = 0;
    int64_t decay_low_rank_dim = 0;
    int64_t gate_low_rank_dim = 0;
    int64_t a_low_rank_dim = 0;
    int64_t v_low_rank_dim = 32;
    int64_t head_dim = 64;
    int64_t num_heads = 0;
};

struct RWKV7TensorSpec {
    std::string source_name;
    std::string target_name;
    rwkvmobile::PthDType dtype = rwkvmobile::PthDType::BFloat16;
    std::vector<int64_t> source_shape;
    std::vector<int64_t> source_stride;
    std::vector<int64_t> target_shape;
    std::string storage_key;
    uint64_t storage_offset = 0;
    uint64_t storage_size = 0;
    TensorTransform transform = TensorTransform::Identity;
    uint64_t elements = 0;
};

struct RWKV7Schema {
    RWKV7Config config;
    std::vector<RWKV7TensorSpec> tensors;
};

RWKV7Schema inspect_rwkv7_pth(const rwkvmobile::PthFile &pth);
std::string rwkv7_config_json(const RWKV7Config &config);
bool read_rwkv7_index(
    const std::string &index_path,
    const std::string &source_path,
    RWKV7Schema &schema,
    std::vector<rwkvmobile::PthTensorInfo> &source_tensors);
void write_rwkv7_index(
    const std::string &index_path,
    const std::string &source_path,
    const RWKV7Schema &schema);

} // namespace rwkvagent

#endif
