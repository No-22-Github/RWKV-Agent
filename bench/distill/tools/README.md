# 蒸馏脚本

所有版本的脚本都放在这里。数据格式各版本大同小异，所以一份脚本跨版本复用，**不要按版本复制**。
新版本有不同的地方，就加参数或在公共模块里加开关。

## 公共模块

| 文件 | 内容 |
| --- | --- |
| `distill_paths.py` | 目录布局的唯一来源：`REPO`、`cases_dir(版本)`、`teacher_script(版本, 批次)`、`case_files()`、`find_case(题号)`、`EXCLUDE_JSONL`。目录再调整只改这一个文件 |
| `casegen.py` | 写题：`Batch(salt, author, version, tool_catalog)` 的 `write_case`，外加 fixture 辅助函数（`lines`、`weather`）和 just-bash sidecar 客户端（`Sidecar`、`check_reference`） |
| `gate.sh <版本> [题号通配]` | S2 闸门：对一个版本的题跑 `bank lint` 和 `bank verify --strict-shape` |

## 出题（每批一个子目录，只放这批题的内容）

| 目录 | 批次 | 说明 |
| --- | --- | --- |
| `b10/` | v1.4 b10 试跑 70 题 | `m2a.py`…`m8b.py` 各管一个题类；`common.py` 只写批次设置。见 [b10/README.md](b10/README.md) |
| `b12/` | v1.41 b12 样板 20 题 | `build.py` 写题并在 sidecar 里跑参考解。见 [b12/README.md](b12/README.md) |

新批次照这个样子：建 `b<NN>/common.py`，用 `casegen.Batch` 写 3–5 行设置，题目内容写在 `m*.py` 里。

## 解题、收集、检查

| 脚本 | 用途 | 首次用于 |
| --- | --- | --- |
| `step.py` | 子 Agent 扮演 student，在真实 harness 里逐步盲解 | v1 b04 |
| `collect.py` | 把 step.py 的解题状态收成老师动作脚本 | v1 b04 |
| `b10_merge.py` | 合并多轮 step.py 结果，保留可重判的失败路径 | v1.4 b10 |
| `b10_check.py` | 终答形态检查（写后回读、长度、Markdown、DONE 行） | v1.4 b10 |
| `classify_failures.py` | 跨 arm 的逐题失败分类（v1.2 轨迹复盘） | v1.2 |

## 数据加工

| 脚本 | 用途 | 首次用于 |
| --- | --- | --- |
| `to_segments.py` | 打包行（text + loss_spans）转成 rwkv_state_tune 的 segments 训练行 | v1.3 |
| `build_v13_suffix.py` · `split_v13.py` | 给渲染行追加 `\n\nUser:` 后缀、按题号哈希切出验证集 | v1.3 |
| `v13_scan.py` · `v13_edit_contracts.py` | 扫描 v1.2 语料、改写答案契约（结果在 `v1.3/data/`） | v1.3 |
| `v13_closeout.py` | 收尾恢复路径（N10）的机械变换 | v1.3 |
| `v14_rewrite_finals.py` · `v14_m1_closeout.py` | b09 终答改写、M8 心算剔除与封顶（工作目录 `v1.4/b09_work/`） | v1.4 |
| `train-1-3.sh` · `test-1-3.sh` | v1.3 state 训练（拷到训练机上跑）与上传跑分 | v1.3 |
