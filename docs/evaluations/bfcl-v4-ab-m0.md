# BFCL v4 A+B M0 预热

状态：完成（按 `bfcl-ab-spec-v3.1` 重新预热）

## 固定版本

- 数据仓库：`ShishirPatil/gorilla`
- 数据 commit：`6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- evaluator：`bfcl-eval==2026.3.23`
- Python：3.12
- 额外依赖：`soundfile==0.14.0`
- 模型目录名：`rwkv-agent-bfcl-ab-v1`

数据集包含 13 个 A+B split：A 组 1390 题，B 组 2251 题，合计 3641 题。

## 判分入口

`scripts/bfcl.py` 在隔离进程内注册本地 decode-only stub，不承担推理，不读取 `possible_answer/`，并继承 evaluator 的官方 AST decode 实现。`underscore_to_dot` 固定为 `false`。

这属于 v3.1 §8 的本地 stub 方案：不修改上游 evaluator，不把 RWKV 注册为官方榜单模型。

## M0 冒烟

用 240 条 `irrelevance` 记录写入空 result，经本地 stub 入口调用官方 evaluator，验证注册名、result 目录、题目 ID 匹配和官方 decoder 闭环。

验证命令：

```bash
./scripts/bfcl.sh evaluate \
  --model rwkv-agent-bfcl-ab-v1 \
  --test-category irrelevance \
  --result-dir runs/bfcl/result \
  --score-dir runs/bfcl/score
```

当前本地结果为 `accuracy=1.0`、`correct_count=240`、`total_count=240`。result、score 和命令输出属于可再生成的运行证据，不提交；`runs/bfcl/` 由 `.gitignore` 忽略。

## 边界

M0 只固定数据、evaluator 和判分入口；尚未执行 v3.1 的 M1 适配器体检、M2 `simple_python` 闭环、抽样冻结或五格矩阵。增强档 §2.2b 的十项参数仍是正式实现前的阻塞决策。

后续正式评分、辅助运行及可比性边界统一追加到 [`bfcl-v4-run-log.md`](bfcl-v4-run-log.md)。
