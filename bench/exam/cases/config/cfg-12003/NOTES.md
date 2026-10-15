## Traps
TR-DECOY：production 小节先出现同名 step_degrees。错解会把生产步进角 3.0 改成 0.5，而示教仍为 2.0，或把两处一起改。

## Reference solution
1. 读取两个模式所在文件。
2. 仅将 teaching 小节 step_degrees 从 2.0 改成 0.5 并暂存。

参考终态（仅列目标文件，原始资料保持原样）：

`设备/机械臂.toml`
```text
[production]
step_degrees = 3.0
speed_percent = 70

[teaching]
step_degrees = 0.5
speed_percent = 15
```

## Why the answer is unique
production 为生产模式，teaching 为示教模式；生产段先出现同名键不能成为修改目标。其余原样的要求包含 production 的 3.0 与两段速度值。

## Scoring boundary
用户要求其余内容原样保留，文件使用 equals，保留所有未授权行、空格及原有换行；最终答复的同义表达与排版不参与评分。
自审记录：参考终态及实质错解的局部检查另存 local/runs/exam-sol20-20261015/config-docs-self-review.json。本题仍为 draft，未调用盲解老师，也未经人工审核。

## Primary review revision

主审反例：TOML 中 0.50 与 0.5 数值等价，原题未明确目标行文本却使用 equals。现将所需目标行写入自然编辑请求，全文判分的文字约定可见；其他配置与原有换行保留。不是为了让老师通过而放宽判分。首轮老师实际把第5行 [teaching] 覆盖为 step_degrees，损坏节结构，其失败仍成立。

## Teacher result

首轮DeepSeek把第5行节标题[teaching]替换成step_degrees = 0.5，正确目标在第6行；随后声称正确不改变实际文件损坏。保留文件内容判分。

EXAM-CANARY-9342ad03
