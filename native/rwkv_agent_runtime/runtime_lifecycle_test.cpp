#include "rwkv_agent_runtime.h"

#include <cassert>
#include <cstring>

int main() {
    assert(rwa_abi_version() == RWA_ABI_VERSION);
    assert(std::strcmp(rwa_status_string(RWA_CANCELLED), "cancelled") == 0);

    rwa_runtime_options options{};
    options.struct_size = sizeof(options);
    options.max_active_batch = 4;
    options.queue_capacity = 8;

    rwa_runtime *runtime = nullptr;
    assert(rwa_runtime_create(&options, &runtime) == RWA_OK);
    assert(runtime != nullptr);
    assert(rwa_runtime_destroy(runtime) == RWA_OK);
    assert(rwa_runtime_destroy(nullptr) == RWA_OK);

    options.struct_size = 0;
    runtime = nullptr;
    assert(rwa_runtime_create(&options, &runtime) == RWA_INVALID_ARGUMENT);
    assert(runtime == nullptr);
    return 0;
}
