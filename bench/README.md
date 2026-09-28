# bench/ 数据清单

> 仓库里所有**数据**（题目、老师脚本、账本、冻结的跑分证据、报告附带的机器可读 json）只放在这里；
> 说明文档与报告在 [`docs/`](../docs/README.md)。最后核对：2026-09-28。

## 入库原则

- **入库**：源数据（手写/起草的题、花钱买且不可复现的老师轨迹）、小而关键的冻结证据、报告引用的 json。
- **不入库**：能从源确定性重建的派生物（训练行 `rows.jsonl`、打包好的训练集）和原始运行（`local/runs/`）。
  例外只有 `distill/scripts/`，理由见其 [README](distill/scripts/README.md)。
- 冻结基线：把最小完整证据（`run.json` / `summary.json` / `trace.jsonl`）复制到 `archive/<name>/`，附 README 写明模型、日期、harness 版本与可比性边界。

## 清单

| 路径 | 内容 | 规模 | 文档 |
| --- | --- | --- | --- |
| `workbank/cases/` | workbank 手写题（10 场景，每题 `case.json` + `verify.py` + `NOTES.md`） | 148 题 / 1.1 MB | [出题手册](../docs/workbank/authoring-guide.md) |
| `workbank/cases-shelved/` | 下架题，不参与跑分 | 5 题 | [README](workbank/cases-shelved/README.md) |
| `workbank/tag-vocab.json` | 场景、task_type、陷阱、禁词的机器可读词表；`rwkv-lab bank lint` 与蒸馏 lint 都读它 | — | [HANDOFF §2](../docs/workbank/HANDOFF.md) |
| `workbank/ledger/` | 题目 / 运行 / 失败标注账本（jsonl） | 1.3 MB | [defect-archive](../docs/workbank/defect-archive.md) |
| `workbank/out/workbank.json` | 由 cases 构建的题库快照 | 0.6 MB | — |
| `workbank/tools/` | 一次性审计工具（Go）及其 testdata | — | — |
| `workbank/reports-data/` | `docs/workbank/reports/` 各报告的机器可读数据 | 0.7 MB | [报告目录](../docs/workbank/reports/) |
| `distill/cases/` | 蒸馏题（5xxx = b01–b03，6xxx = b04） | 759 题 / 2.7 MB | [蒸馏工作流](../docs/distill/distill-workflow.md) |
| `distill/cases-shelved/` | 蒸馏下架题 | 27 题 | — |
| `distill/scripts/` | **老师动作脚本**：任何 harness 版本都能用 `corpus render --script` 重渲染出训练行 | 1.4 MB | [README](distill/scripts/README.md) |
| `distill/batches.jsonl` · `exclude.jsonl` · `tag-map.json` | 批次登记（author 以此为准）、打包排除表、标签映射 | — | [批次报告](../docs/distill/reports/) |
| `distill/tools/` | b04 子 Agent 解题工具 `step.py` / `collect.py` | — | [b04 规格](../docs/distill/distill-b04-glm.md) |
| `distill/audit-20260926/` | 蒸馏审阅的统计与清洗策略 json | — | [审阅报告](../docs/evaluations/distill-audit-20260926/REPORT.md) |
| `archive/v10-baseline/` | v8–v10 boundary 基线（RWKV 13B / DeepSeek v4 Flash） | 5.6 MB | [README](archive/v10-baseline/README.md) |
| `archive/primitive-orig30-snapshot-416b073d/` | Primitive Bench 原始 30 题快照 | — | [README](archive/primitive-orig30-snapshot-416b073d/README.md) |
| `archive/bfcl-v4-e8-qwen-enhanced-base-20260822/` | BFCL v4 E8 Qwen enhanced 对照证据 | — | [README](archive/bfcl-v4-e8-qwen-enhanced-base-20260822/README.md) |

入库数据合计约 16 MB。

## 仓库外：`local/`（gitignored，只在本机）

所有本地产物都收在根目录的 `local/` 下（2026-09-28 起；此前平铺在仓库根）。GitHub 上不存在。
**2026-09-28 之前写的报告**里的 `runs/…`、`bin/…`、`datasets/…` 等路径是当时的写法，一律读作 `local/runs/…` 等，报告本身不改。
`local/go.mod` 让 `go list ./...` 跳过这里零散的 Go 程序，不要删。

| 路径 | 内容 | 能否重建 |
| --- | --- | --- |
| `local/bin/` | 跑分用二进制：`go build -o local/bin/rwkv-cli ./cmd/rwkv-cli`（rwkv-lab 同理） | 能 |
| `local/build/` | 编译中间件：`native/agent-runtime`（cgo 链接它）、MLX 源码、`real-model-test/` 真实模型测试工作区 | 能，`scripts/build-*.sh` |
| `local/dist/` | macOS 发布包：CLI、App、dylib、词表、`build-manifest.json` | 能，`scripts/build-macos.sh`、`build-app.sh` |
| `local/datasets/raw/` | 外部原始语料（toucan、ultradata、nemotron、toolpref 等），约 17 GB | 能，`local/datasets/download_all.sh` |
| `local/datasets/data/` | 清洗后的外部语料（normalized / rendered），约 1.2 GB | 能，按 `local/datasets/data/REPORT.md` |
| `local/datasets/workspace-agent-700-20260920/` | 旧 700 条轨迹制作工作区；`base700` 重渲染需要其中的 `generated/normalized/all.jsonl` | **不能**，另有 `.zip` 备份 |
| `local/outputs/workspace-agent-distill-clean-*` | 交付的训练集（v1.1 / v1.2） | 能，由 `distill/scripts/` + cases 重渲染再 pack |
| `local/outputs/workspace-agent-700*` | 700 条的导出母本与送训 text-only 版 | 能，由 700 工作区导出 |
| `local/runs/` | 所有原始跑分（run.json / trace.jsonl） | 否，但只有冻结进 `archive/` 的才算证据 |
| `local/state_output/` | state 训练扫描产物 | 否 |

## 迁移到 Hugging Face 的边界

现在入库数据量小，先放在仓库里。满足以下任一条件时，把对应目录迁到 HF dataset repo，仓库里只留本表中的指针和 sha256：

- 单个目录超过约 50 MB，或 `bench/` 合计超过约 200 MB；
- 要公开发布训练集（首选迁移 `distill/scripts/` 加一份打包好的 `rows`）。

题目（`*/cases/`）和词表要跟代码版本一起走，建议一直留在仓库里。
