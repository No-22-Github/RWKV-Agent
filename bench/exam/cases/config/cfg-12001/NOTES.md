## Traps
无陷阱；单文件单键的直接修改。

## Reference solution
1. 读取设置文件。
2. 将 autosave_seconds 从 90 改为 45 并暂存，其余内容保留。

参考终态（仅列目标文件，原始资料保持原样）：

`设置/口述转写.ini`
```text
[recorder]
autosave_seconds = 45
input_device = built_in
retain_audio = true
```

## Why the answer is unique
自动存盘只有 autosave_seconds 一个键，用户给定 45 秒，无单位换算或环境歧义。

## Scoring boundary
用户要求其余内容原样保留，文件使用 equals，保留所有未授权行、空格及原有换行；最终答复的同义表达与排版不参与评分。
自审记录：参考终态及实质错解的局部检查另存 local/runs/exam-sol20-20261015/config-docs-self-review.json。本题仍为 draft，未调用盲解老师，也未经人工审核。

EXAM-CANARY-9342ad01
