# 700 条 Agent 数据集导出

本次导出：phase3-repaired-700-20260920；630 train + 70 validation。

- `normalized/all.jsonl`：700 条完整规范化任务、工具轨迹、回执和验收元数据。
- `normalized/train.jsonl` / `validation.jsonl`：630 / 70 条。
- `rendered/none-ctx4096/train.jsonl` / `validation.jsonl`：实际训练文本与 loss_spans、meta，630 / 70 条。
- `hashes.json` / `split-manifest.json`：记录、渲染和分组证据。

训练输入使用 rendered 文件并遵循 loss_spans；normalized 含验收侧信息，不能把其中所有字段拼成模型输入。
实际 tokenizer 长度最大 3352，全部不超过 4096。少量 train 内结构近重复按用户授权保留，详见
`../verification/phase3-retention-policy.json`。正确性、真实回放、mask、协议与 split 检查保持生效。
