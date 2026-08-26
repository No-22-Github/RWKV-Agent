# BFCL v4 产品语义迁移 suite

日期：2026-08-26（Asia/Shanghai）

## 范围

主线新增内置 suite `bfcl-product`，共 60 题。它是产品 Harness 的语义回归集，不是 BFCL 官方成绩，也不加载 BFCL evaluator、JSON anchor 或原始函数目录。

| 分组 | 数量 | 来源与目的 |
| --- | ---: | --- |
| `bfcl-irrelevance` | 20 | 冻结 BFCL v4 `irrelevance` 原题，保留原题文和题目 ID，只验证产品工具目录下的主动不调用 |
| `bfcl-missing-required` | 20 | 10 组缺参/已给参配对；来源标注 BFCL `simple_python` 题 ID，映射到 `read_file`/`search_text` |
| `bfcl-multiturn` | 20 | 10 组状态推进/失败恢复配对；来源标注 BFCL `multi_turn` 题 ID，映射到产品只读工作区 |

BFCL 数据来源固定为 `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。后两组不是把 BFCL 函数名硬塞进产品，而是保留“缺少必要信息”“提供信息后执行”“失败后恢复”“已获得证据后终止调用”这些可迁移语义。

## 运行

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite bfcl-product \
  --output runs/local-bfcl-product
```

可用 `--case bfcl_irrelevance_...` 重跑单题或一组题。suite 的 `summary.json` 应重点查看 `active_no_call`、`no_call_accuracy`、`required_tool_completion`、`required_call_accuracy` 和多轮逐题失败原因；不要把它们汇总成 BFCL leaderboard 分数。

## 后续扩展

先用这 60 题建立产品协议基线，再按失败分布增加题目。扩展仍应保持独立题库、正反配对和单因子 A/B；BFCL 的 `finish_task`、`no_tool`、anchor 字节和官方判分逻辑不直接进入产品默认协议。
