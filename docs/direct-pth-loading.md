# Direct PTH loading

## 目标

RWKV checkpoint 是唯一的持久化权重。运行模型不再要求先生成同等大小的
`model.safetensors`；`convert` 只作为显式导出能力保留。

## 运行链路

```text
rwkv-cli --model model.pth
  → Go backend 探测 ZIP central directory，计算快速语义指纹
  → 计算用户 cache 中的 .rwkvi 路径
  → C ABI rwa_model_load(model_path, tokenizer_path, index_path)
  → C++ mmap PyTorch ZIP checkpoint
  → 冷启动：解析 data.pkl，推断 RWKV-7 config 和 tensor 映射，原子写索引
  → 热启动：校验 size/mtime，从索引恢复 storage key、offset、dtype、shape
  → contiguous tensor 直接以 mmap view 提供给 MLX FFI
  → Swift FFI 包装 MLXArray、执行现有 RWKV-7 sanitize/update
  → MLX / Metal 推理
```

Swift FFI 不读取 `.pth`、不管理索引，也不写模型文件。它只复用现有
`Rwkv7Model` 定义，把 C++ 提供的内存 tensor 装入 MLX。

## 索引

索引位于：

```text
~/Library/Caches/RWKV-Agent/pth-index/v1/<path-hash>.rwkvi
```

内容包括：

- RWKV-7 配置；
- source tensor 到 MLX parameter 的名称映射；
- dtype、source/target shape、stride 和必要的 transpose；
- PyTorch ZIP storage key、storage offset 和 storage size；
- checkpoint size 与 mtime。

索引不包含权重字节。写入使用同目录临时文件和 rename；不存在、损坏或与 checkpoint
元数据不一致时，运行时回退到 `data.pkl`，校验完整 tensor layout 后重建。

## 磁盘与内存边界

- 磁盘：一个原始 `.pth` 加一个通常为几十到几百 KB 的索引。
- 不创建临时 safetensors，不创建第二份模型 cache。
- `.pth` 使用只读 private mmap。
- contiguous tensor 从 mmap 直接交给 MLX；MLX 仍需拥有实际推理权重内存。
- 非 contiguous tensor 才进入安全的 gather/转换 fallback。

## 构建边界

`scripts/build-mlx-ffi.sh` 从固定 upstream commit 构建 MLX FFI，并应用仓库内的
`direct-pth.patch`。最终用户运行的是已链接的静态库和
`librwkv_agent_runtime.dylib`，不需要单独安装 Python、PyTorch 或 Swift package。
