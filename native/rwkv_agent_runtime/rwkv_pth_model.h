#ifndef RWKV_AGENT_PTH_MODEL_H
#define RWKV_AGENT_PTH_MODEL_H

#include <string>

void *rwkv_agent_load_pth_model(
    const std::string &pth_path,
    const std::string &index_path,
    std::string &error);

#endif
