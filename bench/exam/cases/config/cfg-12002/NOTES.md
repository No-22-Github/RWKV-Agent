## Traps
无陷阱；待机亮度与工作亮度的键名均明确，不埋额外环境或旧版干扰。

## Reference solution
1. 读取签到屏配置。
2. 将 IDLE_BRIGHTNESS 从 60 改为 28 并暂存，保留 ACTIVE_BRIGHTNESS=85 等其他行。

参考终态（仅列目标文件，原始资料保持原样）：

`终端/签到屏.env`
```text
KIOSK_LABEL=东侧接待台
IDLE_BRIGHTNESS=28
ACTIVE_BRIGHTNESS=85
SCANNER_PORT=/dev/tty.usbmodem42
```

## Why the answer is unique
题面明确待机亮度，IDLE_BRIGHTNESS 与 ACTIVE_BRIGHTNESS 含义清楚，目标唯一。

## Scoring boundary
用户要求其余内容原样保留，文件使用 equals，保留所有未授权行、空格及原有换行；最终答复的同义表达与排版不参与评分。
自审记录：参考终态及实质错解的局部检查另存 local/runs/exam-sol20-20261015/config-docs-self-review.json。本题仍为 draft，未调用盲解老师，也未经人工审核。

EXAM-CANARY-9342ad02
