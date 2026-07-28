#include "rwkv7_schema.h"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

int main() {
    const auto nonce =
        std::chrono::high_resolution_clock::now().time_since_epoch().count();
    const fs::path directory =
        fs::temp_directory_path() / ("rwkv-agent-index-test-" + std::to_string(nonce));
    const fs::path model_path = directory / "model.pth";
    const fs::path index_path = directory / "model.rwkvi";
    fs::create_directories(directory);

    {
        std::ofstream model(model_path, std::ios::binary);
        model << "checkpoint";
    }

    rwkvagent::RWKV7Schema source;
    source.config.vocab_size = 65536;
    source.config.hidden_size = 2048;
    source.config.intermediate_size = 7168;
    source.config.num_hidden_layers = 24;
    source.config.num_heads = 32;
    rwkvagent::RWKV7TensorSpec tensor;
    tensor.source_name = "emb.weight";
    tensor.target_name = "model.embeddings.weight";
    tensor.dtype = rwkvmobile::PthDType::BFloat16;
    tensor.source_shape = {65536, 2048};
    tensor.source_stride = {2048, 1};
    tensor.target_shape = tensor.source_shape;
    tensor.storage_key = "0";
    tensor.storage_offset = 0;
    tensor.storage_size = 65536ull * 2048ull;
    tensor.elements = tensor.storage_size;
    source.tensors.push_back(tensor);

    try {
        rwkvagent::write_rwkv7_index(
            index_path.string(), model_path.string(), source);
        rwkvagent::RWKV7Schema restored;
        std::vector<rwkvmobile::PthTensorInfo> indexed_tensors;
        if (!rwkvagent::read_rwkv7_index(
                index_path.string(),
                model_path.string(),
                restored,
                indexed_tensors)) {
            std::cerr << "fresh index was not readable\n";
            return 1;
        }
        if (restored.config.hidden_size != source.config.hidden_size ||
            restored.tensors.size() != 1 ||
            restored.tensors[0].target_name != tensor.target_name ||
            indexed_tensors.size() != 1 ||
            indexed_tensors[0].storage_key != "0") {
            std::cerr << "index round trip mismatch\n";
            return 1;
        }

        {
            std::ofstream model(model_path, std::ios::binary | std::ios::app);
            model << "changed";
        }
        if (rwkvagent::read_rwkv7_index(
                index_path.string(),
                model_path.string(),
                restored,
                indexed_tensors)) {
            std::cerr << "stale index was accepted\n";
            return 1;
        }
    } catch (const std::exception &exception) {
        std::cerr << exception.what() << '\n';
        return 1;
    }

    std::error_code ignored;
    fs::remove_all(directory, ignored);
    return 0;
}
