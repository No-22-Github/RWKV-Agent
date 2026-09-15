# BFCL v4 A+B M3 抽样冻结

## 结论

M3 的确定性抽样、v1 冻结清单、运行时过滤与代表性诊断工具已经落地。固定 BFCL 数据共加载 3641 题,按预注册名额选出 351 题;同一数据与代码重复生成时,manifest 逐字节一致。

- 数据 commit:`6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- Manifest:`configs/bfcl-sample-v1.json`
- SHA-256:`65a254807a450991c7d21afb2cf31846abad91e36fb416f5acacc5dfedfd2d71`
- 算法:`bfcl-ab-stratified-hare-v1`
- 分层:工具数 `0–1` / `2–4` / `5+`;原始函数 JSON 总字节数按 split 内 nearest-rank p33/p66 分三档
- 分配:Hare 最大余额法,余数并列按 `(工具档,长度档)` 升序
- 层内:ID 自然序,索引 `floor(j * 层大小 / 层名额)`
- 随机数:不使用

## 产物与命令

生成冻结清单:

```bash
go run ./cmd/rwkv-cli bfcl-sample --output configs/bfcl-sample-v1.json
```

重复生成并逐字节核验:

```bash
go run ./cmd/rwkv-cli bfcl-sample --verify configs/bfcl-sample-v1.json
```

矩阵运行使用同一清单:

```bash
./dist/rwkv-cli bfcl-eval \
  --model <model> \
  --api-url <endpoint> \
  --tier baseline \
  --transport chat-completions-wrapped \
  --split simple_python,simple_java,simple_javascript,multiple,parallel,parallel_multiple,irrelevance,live_simple,live_multiple,live_parallel,live_parallel_multiple,live_relevance,live_irrelevance \
  --sample-manifest configs/bfcl-sample-v1.json \
  --output runs/bfcl/<run-id>
```

`run.json` 会记录清单路径、版本和 SHA-256。

全量 Qwen3-8B 增强档完成官方判分后生成代表性诊断:

```bash
./dist/rwkv-cli bfcl-sampling-diagnostic \
  --manifest configs/bfcl-sample-v1.json \
  --score runs/bfcl/<qwen-enhanced-full>/score \
  --output runs/bfcl/sampling-diagnostic.md
```

诊断器要求每个 split 都是完整官方 score,按逐题失败 ID 从同一次全量运行反推抽样分。若 `|抽样分−全量分| > 2 × 100/n`,它只按预注册规则机械生成 `configs/bfcl-sample-v2.json`;不接受人工改层、换 seed 或多次调样。

## 固定数据边界修正

实现过程中发现原规格的两个数据假设与固定 commit 不符,已修正文档和加载器:

- `live_irrelevance` 有 4 条 `function: []`;空工具仅对 irrelevance 类别合法。
- A+B 范围内有 11 条 assistant 历史消息,全部位于 `live_irrelevance`;加载与 Markdown 渲染保持原顺序和内容。

## 诊断结果

Qwen3-8B 原生 FC 全量参考格已完成，诊断报告为 `runs/bfcl/qwen-native-fc-full-greedy-t0-c48-m4096-sampling-diagnostic-20260819.md`。v1 在 `simple_java`、`live_simple`、`live_irrelevance` 三个 split 超过预注册误差阈值，工具按规则机械生成 v2：

- v2 清单：`configs/bfcl-sample-v2.json`
- v2 SHA-256：`f691e923da092230ca1d6692168fbaabc5425883c29814e9ce028161842b7914`
- 五格矩阵后续统一使用 v2，不人工调整层配额或 seed。
