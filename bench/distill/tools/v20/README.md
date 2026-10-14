# v2.0 流水线脚本（MiSS 带思考数据）

计划见 [distill-allocation-v2.0.md](../../v2.0/distill-allocation-v2.0.md)，出题规格见 [authoring-v2.0.md](../../v2.0/authoring-v2.0.md)。新出的题在各自批次目录（`../b20a`–`../b20d`）。

| 文件 | 作用 |
|---|---|
| `select.py` | 从 1.x 训练包挑 600 道题（b20s），复制成 `<前缀>-2xxxx`，推出 `tool_policy`，去掉隐性字数上限；写 `v2.0/reports/b20s-selection.json` |
| `materialize.py` | 工具目录生成器：按题号定种子，从 `tool_policy` 抽实际目录并打乱，写成运行副本（`offered_tools` + `offered_tools_ordered: true`）和 `toolsets.jsonl` |
| `run_teacher.sh` | 一个批次：抽目录 → 对所有测试集去污染 → DeepSeek（无 suffix、每步思考、work-v2）跑 k 次 |
| `filter.py` | 跑完后的机械过滤（终答长度/语言、只要值题的 Markdown、思考过长、思考谈论指令） |
| `render.sh` | 抽路径（每题 1 条）→ 过滤 → 用 `--profile g1k-think` 按步渲染训练行 |

```bash
# 二进制（需要含 tool_policy / g1k-think 的代码）
go build -o local/bin/rwkv-cli-v20 ./cmd/rwkv-cli
go build -tags chatcompletions -o local/bin/rwkv-cli-chat-v20 ./cmd/rwkv-cli
go build -o local/bin/rwkv-lab-v20 ./cmd/rwkv-lab

python3 bench/distill/tools/v20/select.py                       # 选题（可重跑，逐字节一致）
RWKV_LAB=local/bin/rwkv-lab-v20 bench/distill/tools/gate.sh v2.0  # lint + verify
bench/distill/tools/v20/run_teacher.sh b20s '*-2[5-9]???' 2      # 老师（PARALLEL=并发，默认 12）
bench/distill/tools/v20/render.sh b20s                           # 路径 → 过滤 → 按步渲染
```

产物都在 `local/runs/distill/v20/<批次>/`，不入库。
