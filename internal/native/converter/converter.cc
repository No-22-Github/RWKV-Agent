//go:build cgo && converter

#include "converter.h"

#include "pth_loader.h"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

namespace fs = std::filesystem;

namespace {

enum class Precision {
    BF16,
    FP16,
    FP32,
};

struct TensorSpec {
    std::string source_name;
    std::string target_name;
    std::vector<int64_t> source_shape;
    std::vector<int64_t> target_shape;
    bool transposed = false;
    uint64_t elements = 0;
    uint64_t byte_start = 0;
    uint64_t byte_end = 0;
};

struct ModelConfig {
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

uint64_t dtype_size(Precision precision) {
    return precision == Precision::FP32 ? 4 : 2;
}

std::string dtype_name(Precision precision) {
    switch (precision) {
        case Precision::BF16: return "BF16";
        case Precision::FP16: return "F16";
        case Precision::FP32: return "F32";
    }
    throw std::runtime_error("unknown precision");
}

std::string torch_dtype_name(Precision precision) {
    switch (precision) {
        case Precision::BF16: return "bfloat16";
        case Precision::FP16: return "float16";
        case Precision::FP32: return "float32";
    }
    throw std::runtime_error("unknown precision");
}

Precision parse_precision(const std::string &value) {
    if (value == "bf16") return Precision::BF16;
    if (value == "fp16") return Precision::FP16;
    if (value == "fp32") return Precision::FP32;
    throw std::runtime_error("precision must be bf16, fp16, or fp32");
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

std::pair<std::string, bool> translate_name(const std::string &source, int64_t layers) {
    static const std::map<std::string, std::string> top_level = {
        {"emb.weight", "model.embeddings.weight"},
        {"ln_out.weight", "model.norm.weight"},
        {"ln_out.bias", "model.norm.bias"},
        {"head.weight", "lm_head.weight"},
    };
    const auto top = top_level.find(source);
    if (top != top_level.end()) {
        return {top->second, false};
    }
    if (source == "blocks.0.att.v0" ||
        source == "blocks.0.att.v1" ||
        source == "blocks.0.att.v2") {
        return {"", false};
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

    bool transposed = false;
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
            transposed = index == '1' || index == '2';
        }
    }

    std::ostringstream target;
    target << "model.layers." << layer;
    for (size_t i = 2; i < parts.size(); ++i) {
        target << '.' << parts[i];
    }
    return {target.str(), transposed};
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

ModelConfig infer_config(const rwkvmobile::PthFile &pth) {
    ModelConfig config;
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

std::vector<TensorSpec> build_specs(
    const rwkvmobile::PthFile &pth,
    const ModelConfig &config,
    Precision precision) {
    std::vector<TensorSpec> specs;
    std::unordered_set<std::string> targets;
    for (const auto &source : pth.tensor_names()) {
        const auto *info = pth.get_tensor_info(source);
        if (!info) {
            throw std::runtime_error("tensor metadata disappeared: " + source);
        }
        validate_layout(*info);
        auto [target, transposed] = translate_name(source, config.num_hidden_layers);
        if (target.empty()) {
            continue;
        }
        if (!targets.insert(target).second) {
            throw std::runtime_error("duplicate target tensor: " + target);
        }

        TensorSpec spec;
        spec.source_name = source;
        spec.target_name = target;
        spec.source_shape = info->shape;
        spec.target_shape = info->shape;
        spec.transposed = transposed;
        if (transposed) {
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
            spec.target_shape[2] == config.hidden_size) {
            spec.target_shape = {config.hidden_size};
        }
        spec.elements = element_count(spec.target_shape, target);
        specs.push_back(std::move(spec));
    }

    std::sort(specs.begin(), specs.end(), [](const TensorSpec &left, const TensorSpec &right) {
        return left.target_name < right.target_name;
    });
    uint64_t offset = 0;
    for (auto &spec : specs) {
        spec.byte_start = offset;
        const uint64_t bytes = checked_multiply(spec.elements, dtype_size(precision), spec.target_name);
        if (offset > std::numeric_limits<uint64_t>::max() - bytes) {
            throw std::runtime_error("safetensors offset overflow");
        }
        offset += bytes;
        spec.byte_end = offset;
    }
    if (specs.empty()) {
        throw std::runtime_error("source .pth contains no convertible tensors");
    }
    return specs;
}

std::string shape_json(const std::vector<int64_t> &shape) {
    std::ostringstream out;
    out << '[';
    for (size_t i = 0; i < shape.size(); ++i) {
        if (i) out << ',';
        out << shape[i];
    }
    out << ']';
    return out.str();
}

std::string safetensors_header(
    const std::vector<TensorSpec> &specs,
    Precision precision) {
    std::ostringstream out;
    out << "{\"__metadata__\":{\"format\":\"pt\"}";
    for (const auto &spec : specs) {
        out << ",\"" << spec.target_name << "\":{"
            << "\"dtype\":\"" << dtype_name(precision) << "\","
            << "\"shape\":" << shape_json(spec.target_shape) << ','
            << "\"data_offsets\":[" << spec.byte_start << ',' << spec.byte_end << "]}";
    }
    out << '}';
    std::string header = out.str();
    const size_t padding = (8 - ((8 + header.size()) % 8)) % 8;
    header.append(padding, ' ');
    return header;
}

void write_u64_le(std::ostream &out, uint64_t value) {
    uint8_t bytes[8];
    for (size_t i = 0; i < 8; ++i) {
        bytes[i] = static_cast<uint8_t>((value >> (i * 8)) & 0xffu);
    }
    out.write(reinterpret_cast<const char *>(bytes), sizeof(bytes));
}

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

uint16_t float_to_fp16(float value) {
    half_float::half converted(value);
    uint16_t bits = 0;
    static_assert(sizeof(converted) == sizeof(bits), "unexpected half size");
    std::memcpy(&bits, &converted, sizeof(bits));
    return bits;
}

float output_value(
    const std::vector<float> &source,
    const TensorSpec &spec,
    uint64_t output_index) {
    if (!spec.transposed) {
        return source.at(static_cast<size_t>(output_index));
    }
    const uint64_t rows = static_cast<uint64_t>(spec.source_shape[0]);
    const uint64_t columns = static_cast<uint64_t>(spec.source_shape[1]);
    const uint64_t target_row = output_index / rows;
    const uint64_t target_column = output_index % rows;
    const uint64_t source_index = target_column * columns + target_row;
    return source.at(static_cast<size_t>(source_index));
}

void write_tensor(
    std::ofstream &out,
    const rwkvmobile::PthFile &pth,
    const TensorSpec &spec,
    Precision precision) {
    const std::vector<float> source = pth.read_tensor_float32(spec.source_name);
    if (source.size() != spec.elements) {
        throw std::runtime_error("tensor element count mismatch: " + spec.source_name);
    }
    constexpr uint64_t chunk_elements = 1024 * 1024;
    if (precision == Precision::FP32) {
        std::vector<float> chunk;
        chunk.resize(static_cast<size_t>(std::min(chunk_elements, spec.elements)));
        for (uint64_t start = 0; start < spec.elements; start += chunk_elements) {
            const uint64_t count = std::min(chunk_elements, spec.elements - start);
            for (uint64_t i = 0; i < count; ++i) {
                chunk[static_cast<size_t>(i)] = output_value(source, spec, start + i);
            }
            out.write(
                reinterpret_cast<const char *>(chunk.data()),
                static_cast<std::streamsize>(count * sizeof(float)));
        }
    } else {
        std::vector<uint16_t> chunk;
        chunk.resize(static_cast<size_t>(std::min(chunk_elements, spec.elements)));
        for (uint64_t start = 0; start < spec.elements; start += chunk_elements) {
            const uint64_t count = std::min(chunk_elements, spec.elements - start);
            for (uint64_t i = 0; i < count; ++i) {
                const float value = output_value(source, spec, start + i);
                chunk[static_cast<size_t>(i)] =
                    precision == Precision::BF16 ? float_to_bf16(value) : float_to_fp16(value);
            }
            out.write(
                reinterpret_cast<const char *>(chunk.data()),
                static_cast<std::streamsize>(count * sizeof(uint16_t)));
        }
    }
    if (!out) {
        throw std::runtime_error("failed writing tensor: " + spec.target_name);
    }
}

std::string decimal_ratio(int64_t numerator, int64_t denominator) {
    const double value = static_cast<double>(numerator) / static_cast<double>(denominator);
    std::ostringstream out;
    out << std::fixed << std::setprecision(6) << value;
    std::string result = out.str();
    while (result.size() > 2 && result.back() == '0' && result[result.size() - 2] != '.') {
        result.pop_back();
    }
    return result;
}

void write_config(
    const fs::path &path,
    const ModelConfig &config,
    Precision precision) {
    std::ofstream out(path, std::ios::binary | std::ios::trunc);
    if (!out) {
        throw std::runtime_error("failed to create config.json");
    }
    out << "{\n"
        << "  \"model_type\": \"rwkv7\",\n"
        << "  \"architect\": [\"RWKV7ForCausalLM\"],\n"
        << "  \"auto_map\": {\n"
        << "    \"AutoConfig\": \"fla.models.rwkv7.configuration_rwkv7.RWKV7Config\",\n"
        << "    \"AutoModelForCausalLM\": \"fla.models.rwkv7.modeling_rwkv7.RWKV7ForCausalLM\"\n"
        << "  },\n"
        << "  \"attn_mode\": \"chunk\",\n"
        << "  \"hidden_size\": " << config.hidden_size << ",\n"
        << "  \"hidden_ratio\": " << decimal_ratio(config.intermediate_size, config.hidden_size) << ",\n"
        << "  \"intermediate_size\": " << config.intermediate_size << ",\n"
        << "  \"num_hidden_layers\": " << config.num_hidden_layers << ",\n"
        << "  \"head_dim\": " << config.head_dim << ",\n"
        << "  \"num_heads\": " << config.num_heads << ",\n"
        << "  \"decay_low_rank_dim\": " << config.decay_low_rank_dim << ",\n"
        << "  \"gate_low_rank_dim\": " << config.gate_low_rank_dim << ",\n"
        << "  \"a_low_rank_dim\": " << config.a_low_rank_dim << ",\n"
        << "  \"v_low_rank_dim\": " << config.v_low_rank_dim << ",\n"
        << "  \"value_dim\": [";
    for (int64_t i = 0; i < config.num_hidden_layers; ++i) {
        if (i) out << ", ";
        out << config.hidden_size;
    }
    out << "],\n"
        << "  \"hidden_act\": \"sqrelu\",\n"
        << "  \"max_position_embeddings\": 2048,\n"
        << "  \"norm_first\": true,\n"
        << "  \"norm_bias\": true,\n"
        << "  \"norm_eps\": 1e-05,\n"
        << "  \"use_cache\": true,\n"
        << "  \"tie_word_embeddings\": false,\n"
        << "  \"fuse_norm\": true,\n"
        << "  \"fuse_cross_entropy\": true,\n"
        << "  \"fuse_linear_cross_entropy\": false,\n"
        << "  \"use_l2warp\": true,\n"
        << "  \"vocab_size\": " << config.vocab_size << ",\n"
        << "  \"torch_dtype\": \"" << torch_dtype_name(precision) << "\",\n"
        << "  \"bos_token_id\": 0,\n"
        << "  \"eos_token_id\": 0,\n"
        << "  \"pad_token_id\": 0\n"
        << "}\n";
    if (!out) {
        throw std::runtime_error("failed writing config.json");
    }
}

fs::path unique_sibling(const fs::path &output, const std::string &label) {
    const auto stamp = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    return output.parent_path() /
        ("." + output.filename().string() + ".rwkv-agent-" + label + "-" + std::to_string(stamp));
}

void commit_directory(const fs::path &stage, const fs::path &output, bool overwrite) {
    if (!fs::exists(output)) {
        fs::rename(stage, output);
        return;
    }
    if (!overwrite) {
        throw std::runtime_error("output path already exists; pass --overwrite to replace it");
    }
    if (!fs::is_directory(output)) {
        throw std::runtime_error("output path exists and is not a directory");
    }

    const fs::path backup = unique_sibling(output, "backup");
    fs::rename(output, backup);
    try {
        fs::rename(stage, output);
    } catch (...) {
        fs::rename(backup, output);
        throw;
    }
    std::error_code ignored;
    fs::remove_all(backup, ignored);
}

void convert(
    const fs::path &input,
    const fs::path &output,
    const fs::path &tokenizer,
    Precision precision,
    bool overwrite) {
    if (!fs::is_regular_file(input)) {
        throw std::runtime_error("input .pth does not exist or is not a file");
    }
    if (!fs::is_regular_file(tokenizer)) {
        throw std::runtime_error("RWKV World tokenizer does not exist or is not a file");
    }
    fs::path parent = output.parent_path();
    if (parent.empty()) {
        parent = fs::current_path();
    }
    fs::create_directories(parent);
    if (fs::exists(output) && !overwrite) {
        throw std::runtime_error("output path already exists; pass --overwrite to replace it");
    }

    std::cerr << "Reading native RWKV .pth metadata...\n";
    rwkvmobile::PthFile pth(input.string());
    const ModelConfig config = infer_config(pth);
    std::vector<TensorSpec> specs = build_specs(pth, config, precision);
    const uint64_t weight_bytes = specs.back().byte_end;
    const uint64_t reserve = std::max<uint64_t>(64 * 1024 * 1024, weight_bytes / 20);
    const auto available = fs::space(parent).available;
    if (available < weight_bytes + reserve) {
        throw std::runtime_error(
            "insufficient disk space: need approximately " +
            std::to_string((weight_bytes + reserve) / 1000000) + " MB");
    }

    std::cerr
        << "Inferred RWKV-7: layers=" << config.num_hidden_layers
        << " hidden=" << config.hidden_size
        << " vocab=" << config.vocab_size
        << " tensors=" << specs.size() << '\n';

    const fs::path stage = unique_sibling(output, "convert");
    fs::create_directory(stage);
    bool committed = false;
    try {
        const fs::path weights_path = stage / "model.safetensors";
        std::ofstream weights(weights_path, std::ios::binary | std::ios::trunc);
        if (!weights) {
            throw std::runtime_error("failed to create model.safetensors");
        }
        const std::string header = safetensors_header(specs, precision);
        write_u64_le(weights, static_cast<uint64_t>(header.size()));
        weights.write(header.data(), static_cast<std::streamsize>(header.size()));

        for (size_t i = 0; i < specs.size(); ++i) {
            if (i == 0 || i + 1 == specs.size() || (i + 1) % std::max<size_t>(1, specs.size() / 20) == 0) {
                std::cerr << "\rConverting tensor " << (i + 1) << '/' << specs.size() << std::flush;
            }
            write_tensor(weights, pth, specs[i], precision);
        }
        std::cerr << '\n';
        weights.flush();
        if (!weights) {
            throw std::runtime_error("failed finalizing model.safetensors");
        }
        weights.close();

        const uint64_t expected_size = 8 + header.size() + weight_bytes;
        if (fs::file_size(weights_path) != expected_size) {
            throw std::runtime_error("safetensors output size validation failed");
        }
        write_config(stage / "config.json", config, precision);
        fs::copy_file(
            tokenizer,
            stage / "rwkv_vocab_v20230424.txt",
            fs::copy_options::overwrite_existing);

        commit_directory(stage, output, overwrite);
        committed = true;
    } catch (...) {
        if (!committed) {
            std::error_code ignored;
            fs::remove_all(stage, ignored);
        }
        throw;
    }

    std::cerr << "Conversion complete: " << output << '\n';
}

} // namespace

extern "C" int rwkv_agent_convert_pth(
    const char *input_path,
    const char *output_path,
    const char *tokenizer_path,
    const char *precision,
    int overwrite,
    char *error_buffer,
    size_t error_capacity) {
    if (error_buffer && error_capacity > 0) {
        error_buffer[0] = '\0';
    }
    try {
        if (!input_path || !output_path || !tokenizer_path || !precision) {
            throw std::runtime_error("converter received a null path or precision");
        }
        convert(
            fs::path(input_path),
            fs::path(output_path),
            fs::path(tokenizer_path),
            parse_precision(precision),
            overwrite != 0);
        return 0;
    } catch (const std::exception &error) {
        if (error_buffer && error_capacity > 0) {
            const std::string message = error.what();
            const size_t count = std::min(error_capacity - 1, message.size());
            std::memcpy(error_buffer, message.data(), count);
            error_buffer[count] = '\0';
        }
        return -1;
    } catch (...) {
        const char *message = "unknown native converter failure";
        if (error_buffer && error_capacity > 0) {
            const size_t count = std::min(error_capacity - 1, std::strlen(message));
            std::memcpy(error_buffer, message, count);
            error_buffer[count] = '\0';
        }
        return -2;
    }
}
