# 数据仓库 `bench/`

2026-10-31 起，本仓库只放代码和文档。题目、考卷、蒸馏源数据、老师轨迹、账本、冻结证据都在 **`bench/`**：
它是一个**独立的 git 仓库**，放在本仓库根目录下，被本仓库的 `.gitignore` 忽略。
路径没有变，代码、脚本、技能文档里写的 `bench/...` 照旧可用。

拆出去的原因：数据量还会大幅增长，而且不同来源的许可证不一样，和代码混在一个仓库里不好管。

## 目录与去向

| `bench/` 下 | 内容 | 公开到 |
| --- | --- | --- |
| `exam/` `workbank/` `bashprobe/` `weatherprobe/` `holdout/` | 考卷与题库、词表 `workbank/tag-vocab.json`、账本 | [No-22/rwkv-agent-exam](https://huggingface.co/datasets/No-22/rwkv-agent-exam)，目录原样 |
| `distill/` | 各版本出题、老师轨迹、报告、蒸馏脚本、`common/`（含 `tag-map.json`） | [No-22/rwkv-agent-distill](https://huggingface.co/datasets/No-22/rwkv-agent-distill) 的 `source/`，目录原样；打包好的训练集在同仓库 `<版本>/dataset/` |
| `archive/` | 冻结的旧跑分证据、700 条轨迹导出集 | 不公开，只在本机和移动硬盘归档 |

`bench/README.md` 是数据仓库自己的清单。

## 怎么拿到数据

- **本机**：`bench/` 已经就位，历史从 `bench/` 建立时（2026-09-17）开始保留。
- **新机器**：在本仓库根目录下把数据放到 `bench/`。可以从本机复制，也可以从 Hugging Face 拉公开部分：

```bash
hf download No-22/rwkv-agent-exam --repo-type dataset --local-dir bench
```

```bash
hf download No-22/rwkv-agent-distill --repo-type dataset --include 'source/*' --local-dir local/hf-distill
```

  第二条下载完后，把 `local/hf-distill/source/` 移到 `bench/distill/`。HF 上没有 `archive/`，依赖它的测试会自动跳过。
- 想把数据放在别处，就让 `bench` 成为指向那里的软链接。

## 版本

- 数据的版本就是 `bench/` 仓库的提交号。改数据在 `bench/` 里提交，改代码在本仓库提交，两边互不牵连。
- 考卷内容另有 hash 钉死：`run.json` 里的 `exam_hash` 只看题号和 `case.json` 内容，所以挪目录不影响可比性，改题才会变（见 `bench/exam/versions.json`）。
- 训练包靠 HF 上的 `SHA256SUMS` 和报告里写的 sha 对应。

## 没有 `bench/` 时

- `go test ./...` 能通过：读数据的测试会用 `t.Skip` 跳过（`internal/lab/labtest.RequireBench`）。lint 的规则测试用的是 `internal/lab/bank/testdata/` 里冻结的一份词表和 3 道样题，不依赖 `bench/`。
- `scripts/check-doc-links.py` 在 `bench/` 存在时会检查指向它的链接，不存在时跳过。
- 跑分、`rwkv-lab exam`、`corpus render` 这类命令需要 `bench/`。

## 上传规则

- 公开前先扫一遍内网地址（`100.64.x.x`）、端点地址和密钥，再用 `hf upload` 上传对应子目录。上传的是文件，不推送 git 历史，所以 HF 上只有当前版本的文件。
- 外部来源的数据（例如 think-sft 用到的 WildChat）在 HF 数据卡里按目录写明来源和许可证。
