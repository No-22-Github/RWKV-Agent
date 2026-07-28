#include "rwkv7_schema.h"

#include <algorithm>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <unordered_set>

namespace fs = std::filesystem;

namespace rwkvagent {
namespace {

uint64_t checked_multiply(uint64_t left, uint64_t right, const std::string &context) {
    if (left != 0 && right > std::numeric_limits<uint64_t>::max() / left) {
        throw std::runtime_error("integer overflow while computing " + context);
    }
    return left * right;
}

uint64_t element_count(const std::vector<int64_t> &shape, const std::string &name) {
    uint64_t count = 1;
    for (int64_t dim : shape) {
        if (dim < 0) {
            throw std::runtime_error("negative tensor dimension: " + name);
        }
        count = checked_multiply(count, static_cast<uint64_t>(dim), name);
    }
    return count;
}

std::vector<std::string> split(const std::string &value, char delimiter) {
    std::vector<std::string> parts;
    std::stringstream stream(value);
    std::string part;
    while (std::getline(stream, part, delimiter)) {
        parts.push_back(part);
    }
    return parts;
}

std::pair<std::string, TensorTransform> translate_name(
    const std::string &source,
    int64_t layers) {
    static const std::map<std::string, std::string> top_level = {
        {"emb.weight", "model.embeddings.weight"},
        {"ln_out.weight", "model.norm.weight"},
        {"ln_out.bias", "model.norm.bias"},
        {"head.weight", "lm_head.weight"},
    };
    const auto top = top_level.find(source);
    if (top != top_level.end()) {
        return {top->second, TensorTransform::Identity};
    }
    if (source == "blocks.0.att.v0" ||
        source == "blocks.0.att.v1" ||
        source == "blocks.0.att.v2") {
        return {"", TensorTransform::Identity};
    }

    auto parts = split(source, '.');
    if (parts.size() < 4 || parts[0] != "blocks") {
        throw std::runtime_error("unsupported RWKV tensor name: " + source);
    }
    int64_t layer = 0;
    try {
        layer = std::stoll(parts[1]);
    } catch (...) {
        throw std::runtime_error("invalid layer in tensor name: " + source);
    }
    if (layer < 0 || layer >= layers) {
        throw std::runtime_error("layer index out of range: " + source);
    }

    if (parts[2] == "att") {
        parts[2] = "attn";
    } else if (parts[2] == "ln0") {
        parts[2] = "pre_norm";
    } else if (parts[2] == "ln1") {
        parts[2] = "attn_norm";
    } else if (parts[2] == "ln2") {
        parts[2] = "ffn_norm";
    } else if (parts[2] != "ffn") {
        throw std::runtime_error("unsupported RWKV block tensor: " + source);
    }

    TensorTransform transform = TensorTransform::Identity;
    if (parts[2] == "attn") {
        static const std::map<std::string, std::string> projections = {
            {"receptance", "r_proj"},
            {"key", "k_proj"},
            {"value", "v_proj"},
            {"output", "o_proj"},
            {"ln_x", "g_norm"},
        };
        const auto projection = projections.find(parts[3]);
        if (projection != projections.end()) {
            parts[3] = projection->second;
        } else if (parts[3].size() == 2 &&
                   std::string("wvag").find(parts[3][0]) != std::string::npos &&
                   parts[3][1] >= '0' && parts[3][1] <= '2') {
            const char kind = parts[3][0];
            const char index = parts[3][1];
            const std::string suffix =
                index == '0' ? "2.bias" :
                index == '1' ? "0.weight" :
                               "2.weight";
            parts[3] = std::string(1, kind) + "_lora.lora." + suffix;
            if (index == '1' || index == '2') {
                transform = TensorTransform::Transpose2D;
            }
        }
    }

    std::ostringstream target;
    target << "model.layers." << layer;
    for (size_t i = 2; i < parts.size(); ++i) {
        target << '.' << parts[i];
    }
    return {target.str(), transform};
}

const rwkvmobile::PthTensorInfo &required_info(
    const rwkvmobile::PthFile &pth,
    const std::string &name) {
    const auto *info = pth.get_tensor_info(name);
    if (!info) {
        throw std::runtime_error("source .pth is missing required tensor: " + name);
    }
    return *info;
}

int64_t shape_at(
    const rwkvmobile::PthTensorInfo &info,
    size_t index,
    const std::string &name) {
    if (index >= info.shape.size()) {
        throw std::runtime_error("unexpected tensor rank: " + name);
    }
    return info.shape[index];
}

RWKV7Config infer_config(const rwkvmobile::PthFile &pth) {
    RWKV7Config config;
    while (pth.has_tensor(
        "blocks." + std::to_string(config.num_hidden_layers) + ".ffn.key.weight")) {
        ++config.num_hidden_layers;
    }
    if (config.num_hidden_layers == 0) {
        throw std::runtime_error("source .pth has no RWKV-7 blocks");
    }

    const auto &emb = required_info(pth, "emb.weight");
    const auto &ffn = required_info(pth, "blocks.0.ffn.key.weight");
    const auto &decay = required_info(pth, "blocks.0.att.w1");
    const auto &gate = required_info(pth, "blocks.0.att.g1");
    const auto &a = required_info(pth, "blocks.0.att.a1");
    config.vocab_size = shape_at(emb, 0, "emb.weight");
    config.intermediate_size = shape_at(ffn, 0, "blocks.0.ffn.key.weight");
    config.hidden_size = shape_at(ffn, 1, "blocks.0.ffn.key.weight");
    config.decay_low_rank_dim = shape_at(decay, 1, "blocks.0.att.w1");
    config.gate_low_rank_dim = shape_at(gate, 1, "blocks.0.att.g1");
    config.a_low_rank_dim = shape_at(a, 1, "blocks.0.att.a1");
    if (const auto *v = pth.get_tensor_info("blocks.1.att.v1")) {
        config.v_low_rank_dim = shape_at(*v, 1, "blocks.1.att.v1");
    }
    if (config.hidden_size <= 0 || config.hidden_size % config.head_dim != 0) {
        throw std::runtime_error("hidden size is not divisible by RWKV-7 head size 64");
    }
    config.num_heads = config.hidden_size / config.head_dim;
    return config;
}

void validate_layout(const rwkvmobile::PthTensorInfo &info) {
    if (info.shape.size() != info.stride.size()) {
        throw std::runtime_error("shape/stride rank mismatch: " + info.name);
    }
    if (info.offset > info.storage_size) {
        throw std::runtime_error("storage offset out of bounds: " + info.name);
    }
    if (std::any_of(info.shape.begin(), info.shape.end(), [](int64_t value) { return value < 0; }) ||
        std::any_of(info.stride.begin(), info.stride.end(), [](int64_t value) { return value < 0; })) {
        throw std::runtime_error("negative shape or stride: " + info.name);
    }
    if (std::any_of(info.shape.begin(), info.shape.end(), [](int64_t value) { return value == 0; })) {
        return;
    }
    uint64_t max_index = info.offset;
    for (size_t i = 0; i < info.shape.size(); ++i) {
        const uint64_t extent = checked_multiply(
            static_cast<uint64_t>(info.shape[i] - 1),
            static_cast<uint64_t>(info.stride[i]),
            info.name);
        if (max_index > std::numeric_limits<uint64_t>::max() - extent) {
            throw std::runtime_error("storage index overflow: " + info.name);
        }
        max_index += extent;
    }
    if (max_index >= info.storage_size) {
        throw std::runtime_error("tensor storage range out of bounds: " + info.name);
    }
}

bool source_identity(
    const std::string &source_path,
    uint64_t &size,
    int64_t &mtime_ticks) {
    std::error_code ec;
    size = fs::file_size(source_path, ec);
    if (ec) return false;
    const auto mtime = fs::last_write_time(source_path, ec);
    if (ec) return false;
    mtime_ticks = static_cast<int64_t>(mtime.time_since_epoch().count());
    return true;
}

void write_shape(std::ostream &out, const std::vector<int64_t> &shape) {
    out << ' ' << shape.size();
    for (int64_t dimension : shape) out << ' ' << dimension;
}

bool read_shape(std::istream &in, std::vector<int64_t> &shape) {
    size_t rank = 0;
    if (!(in >> rank) || rank > 8) return false;
    shape.resize(rank);
    for (auto &dimension : shape) {
        if (!(in >> dimension) || dimension < 0) return false;
    }
    return true;
}

} // namespace

RWKV7Schema inspect_rwkv7_pth(const rwkvmobile::PthFile &pth) {
    RWKV7Schema schema;
    schema.config = infer_config(pth);
    std::unordered_set<std::string> targets;
    for (const auto &source : pth.tensor_names()) {
        const auto *info = pth.get_tensor_info(source);
        if (!info) {
            throw std::runtime_error("tensor metadata disappeared: " + source);
        }
        validate_layout(*info);
        auto [target, transform] = translate_name(source, schema.config.num_hidden_layers);
        if (target.empty()) {
            continue;
        }
        if (!targets.insert(target).second) {
            throw std::runtime_error("duplicate target tensor: " + target);
        }

        RWKV7TensorSpec spec;
        spec.source_name = source;
        spec.target_name = target;
        spec.dtype = info->dtype;
        spec.source_shape = info->shape;
        spec.source_stride = info->stride;
        spec.target_shape = info->shape;
        spec.storage_key = info->storage_key;
        spec.storage_offset = info->offset;
        spec.storage_size = info->storage_size;
        spec.transform = transform;
        if (transform == TensorTransform::Transpose2D) {
            if (spec.target_shape.size() != 2) {
                throw std::runtime_error("transposed LoRA tensor is not rank 2: " + source);
            }
            std::reverse(spec.target_shape.begin(), spec.target_shape.end());
        }
        const bool is_x = target.find("attn.x_") != std::string::npos;
        if (!is_x &&
            spec.target_shape.size() == 3 &&
            spec.target_shape[0] == 1 &&
            spec.target_shape[1] == 1 &&
            spec.target_shape[2] == schema.config.hidden_size) {
            spec.target_shape = {schema.config.hidden_size};
        }
        spec.elements = element_count(spec.target_shape, target);
        schema.tensors.push_back(std::move(spec));
    }
    std::sort(
        schema.tensors.begin(),
        schema.tensors.end(),
        [](const RWKV7TensorSpec &left, const RWKV7TensorSpec &right) {
            return left.target_name < right.target_name;
        });
    if (schema.tensors.empty()) {
        throw std::runtime_error("source .pth contains no RWKV-7 tensors");
    }
    return schema;
}

std::string rwkv7_config_json(const RWKV7Config &config) {
    std::ostringstream out;
    out << '{'
        << "\"model_type\":\"rwkv7\","
        << "\"vocab_size\":" << config.vocab_size << ','
        << "\"hidden_size\":" << config.hidden_size << ','
        << "\"intermediate_size\":" << config.intermediate_size << ','
        << "\"num_hidden_layers\":" << config.num_hidden_layers << ','
        << "\"head_dim\":" << config.head_dim << ','
        << "\"num_heads\":" << config.num_heads << ','
        << "\"decay_low_rank_dim\":" << config.decay_low_rank_dim << ','
        << "\"gate_low_rank_dim\":" << config.gate_low_rank_dim << ','
        << "\"a_low_rank_dim\":" << config.a_low_rank_dim << ','
        << "\"v_low_rank_dim\":" << config.v_low_rank_dim << ','
        << "\"norm_eps\":1e-05,"
        << "\"tie_word_embeddings\":false"
        << '}';
    return out.str();
}

bool read_rwkv7_index(
    const std::string &index_path,
    const std::string &source_path,
    RWKV7Schema &schema,
    std::vector<rwkvmobile::PthTensorInfo> &source_tensors) {
    if (index_path.empty()) return false;
    std::ifstream in(index_path, std::ios::binary);
    if (!in) return false;
    try {
        std::string magic;
        int version = 0;
        uint64_t indexed_size = 0;
        int64_t indexed_mtime = 0;
        if (!(in >> magic >> version) ||
            magic != "RWKV_AGENT_PTH_INDEX" ||
            version != 1 ||
            !(in >> indexed_size >> indexed_mtime)) {
            return false;
        }
        uint64_t actual_size = 0;
        int64_t actual_mtime = 0;
        if (!source_identity(source_path, actual_size, actual_mtime) ||
            indexed_size != actual_size ||
            indexed_mtime != actual_mtime) {
            return false;
        }
        auto &config = schema.config;
        if (!(in >> config.vocab_size
              >> config.hidden_size
              >> config.intermediate_size
              >> config.num_hidden_layers
              >> config.decay_low_rank_dim
              >> config.gate_low_rank_dim
              >> config.a_low_rank_dim
              >> config.v_low_rank_dim
              >> config.head_dim
              >> config.num_heads)) {
            return false;
        }
        size_t count = 0;
        if (!(in >> count) || count == 0 || count > 100000) return false;
        schema.tensors.clear();
        source_tensors.clear();
        schema.tensors.reserve(count);
        source_tensors.reserve(count);
        for (size_t i = 0; i < count; ++i) {
            RWKV7TensorSpec spec;
            int dtype = -1;
            int transform = -1;
            if (!(in >> std::quoted(spec.source_name)
                  >> std::quoted(spec.target_name)
                  >> dtype
                  >> transform
                  >> spec.elements
                  >> spec.storage_offset
                  >> spec.storage_size
                  >> std::quoted(spec.storage_key)) ||
                dtype < 0 || dtype > 2 ||
                transform < 0 || transform > 1 ||
                spec.source_name.empty() ||
                spec.target_name.empty() ||
                spec.storage_key.empty() ||
                !read_shape(in, spec.source_shape) ||
                !read_shape(in, spec.source_stride) ||
                !read_shape(in, spec.target_shape)) {
                return false;
            }
            spec.dtype = static_cast<rwkvmobile::PthDType>(dtype);
            spec.transform = static_cast<TensorTransform>(transform);
            rwkvmobile::PthTensorInfo info;
            info.name = spec.source_name;
            info.dtype = spec.dtype;
            info.shape = spec.source_shape;
            info.stride = spec.source_stride;
            info.offset = spec.storage_offset;
            info.storage_size = spec.storage_size;
            info.storage_key = spec.storage_key;
            source_tensors.push_back(std::move(info));
            schema.tensors.push_back(std::move(spec));
        }
        return true;
    } catch (...) {
        schema = {};
        source_tensors.clear();
        return false;
    }
}

void write_rwkv7_index(
    const std::string &index_path,
    const std::string &source_path,
    const RWKV7Schema &schema) {
    if (index_path.empty()) return;
    const fs::path destination(index_path);
    fs::create_directories(destination.parent_path());
    const auto stamp = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    const fs::path stage = destination.string() + ".tmp-" + std::to_string(stamp);

    uint64_t source_size = 0;
    int64_t mtime_ticks = 0;
    if (!source_identity(source_path, source_size, mtime_ticks)) {
        throw std::runtime_error("stat .pth for index failed");
    }
    std::error_code ec;

    std::ofstream out(stage, std::ios::binary | std::ios::trunc);
    if (!out) {
        throw std::runtime_error("create PTH index failed");
    }
    const auto &config = schema.config;
    out << "RWKV_AGENT_PTH_INDEX 1\n"
        << source_size << ' ' << mtime_ticks << '\n'
        << config.vocab_size << ' '
        << config.hidden_size << ' '
        << config.intermediate_size << ' '
        << config.num_hidden_layers << ' '
        << config.decay_low_rank_dim << ' '
        << config.gate_low_rank_dim << ' '
        << config.a_low_rank_dim << ' '
        << config.v_low_rank_dim << ' '
        << config.head_dim << ' '
        << config.num_heads << '\n'
        << schema.tensors.size() << '\n';
    for (const auto &tensor : schema.tensors) {
        out << std::quoted(tensor.source_name) << ' '
            << std::quoted(tensor.target_name) << ' '
            << static_cast<int>(tensor.dtype) << ' '
            << static_cast<int>(tensor.transform) << ' '
            << tensor.elements << ' '
            << tensor.storage_offset << ' '
            << tensor.storage_size << ' '
            << std::quoted(tensor.storage_key);
        write_shape(out, tensor.source_shape);
        write_shape(out, tensor.source_stride);
        write_shape(out, tensor.target_shape);
        out << '\n';
    }
    out.flush();
    if (!out) {
        std::error_code ignored;
        fs::remove(stage, ignored);
        throw std::runtime_error("write PTH index failed");
    }
    out.close();
    fs::rename(stage, destination, ec);
    if (ec) {
        fs::remove(destination, ec);
        ec.clear();
        fs::rename(stage, destination, ec);
    }
    if (ec) {
        std::error_code ignored;
        fs::remove(stage, ignored);
        throw std::runtime_error("commit PTH index failed: " + ec.message());
    }
}

} // namespace rwkvagent
