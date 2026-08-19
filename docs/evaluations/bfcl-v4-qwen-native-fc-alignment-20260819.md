# BFCL v4 Qwen3-8B Native FC 对齐

## 结论

Qwen/Qwen3-8B-FP8 通过 RWKV-Agent 原生 Chat Completions tools 路径完成 BFCL v4 A+B 全量 3641 题，并使用固定 `bfcl-eval==2026.3.23` 评分。完整合并格为 3503 条首轮成功结果加 138 条 timeout 补跑结果，最终基础设施失败 0、跳过 0。

- Endpoint: `http://192.168.1.112:8000/v1/chat/completions`
- Model: `Qwen/Qwen3-8B-FP8`
- Transport: `chat-completions-native-fc`
- Sampling: `temperature=0`（服务端 greedy），`top_k=1` 记录但未发送 provider 扩展
- Max completion tokens: 4096
- Concurrency: 48
- Per-case timeout: 10m；HTTP client timeout: 11m
- Generation wall time: 1h14m10s；补跑 138 题 12m39s
- Complete artifacts: `runs/bfcl/qwen-native-fc-full-greedy-t0-c48-m4096-complete-20260819`
- Score: `runs/bfcl/qwen-native-fc-full-greedy-t0-c48-m4096-complete-20260819/score`

## Official comparison

Official values were retrieved from:

- <https://gorilla.cs.berkeley.edu/data_non_live.csv>
- <https://gorilla.cs.berkeley.edu/data_live.csv>

The matching row is `Qwen3-8B (FC)`; values retrieved on 2026-08-19.

| Split | Local | Official | Delta |
|---|---:|---:|---:|
| `simple_python` | 94.75% | 95.50% | -0.75pp |
| `simple_java` | 59.00% | 61.00% | -2.00pp |
| `simple_javascript` | 68.00% | 62.00% | +6.00pp |
| `multiple` | 97.00% | 96.50% | +0.50pp |
| `parallel` | 91.50% | 92.00% | -0.50pp |
| `parallel_multiple` | 89.00% | 89.00% | +0.00pp |
| `irrelevance` | 81.25% | 81.67% | -0.42pp |
| `live_simple` | 86.43% | 84.50% | +1.93pp |
| `live_multiple` | 78.73% | 79.68% | -0.95pp |
| `live_parallel` | 81.25% | 75.00% | +6.25pp |
| `live_parallel_multiple` | 66.67% | 79.17% | -12.50pp |
| `live_relevance` | 93.75% | 93.75% | +0.00pp |
| `live_irrelevance` | 76.36% | 76.47% | -0.11pp |

Non-live overall is 87.85%; live overall is 80.01%. The native adapter is within 2pp on the core simple/multiple/parallel/irrelevance splits. The only material outlier is `live_parallel_multiple`, where the local result is 12.50pp below the public row and needs a focused protocol/model investigation before claiming full official parity.

## Determinism and concurrency

The server accepts exact `temperature=0` without the vLLM `<0.01` clamp warning. It does not, however, make FP8 dynamic batching byte-deterministic:

| Probe | Repeat-identical results | Cross-concurrency identical results |
|---|---:|---:|
| `temperature=0`, c16 | 84/96 (87.50%) | — |
| `temperature=0`, c48 | 81/96 (84.38%) | 86/96 and 81/96 |
| `temperature=0.01`, explicit `top_k=1`, c16 | 85/96 (88.54%) | — |
| `temperature=0.01`, explicit `top_k=1`, c48 | 77/96 (80.21%) | 82/96 and 83/96 |

Therefore 48 concurrency is a throughput choice, not a determinism fix. `temperature=0` is the semantically clean formal setting; explicit `top_k=1` did not improve stability and was slower in the c16 probe.

## Reliability fixes

The first c48 full run produced 138 failures, all caused by the Chat Completions SDK's default 2-minute HTTP client timeout while the runner allowed 10 minutes. The failed IDs were rerun with an 11-minute HTTP timeout and all 138 completed successfully. Zero-tool `live_irrelevance` requests now send `tool_choice=none` instead of an invalid tool choice without tools.

The complete score must be read from the merged artifact above; the initial c48 directory is diagnostic-only because it contains the pre-retry timeout failures.
