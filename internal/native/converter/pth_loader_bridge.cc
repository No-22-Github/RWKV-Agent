//go:build cgo && converter

// Compile rwkv-mobile's native PyTorch ZIP/pickle reader into the converter
// without modifying the pinned upstream submodule.
#include "../../../third_party/rwkv-mobile/src/pth_loader.cpp"
