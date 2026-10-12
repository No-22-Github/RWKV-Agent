## Traps
- Turn 1: exact answer 01:34:24; the loose reading (接口前缀匹配，含/pay/refund) gives 17:46:51. Several rows share the extreme value; file order would give 19:48:09, the README rule gives 01:34:24.
- Turn 2: exact answer 00:31:52; the loose reading (接口前缀匹配，含/order/list) gives 04:29:59. Several rows share the extreme value; file order would give 06:38:17, the README rule gives 00:31:52.
- TR-TRUNC: the file is 60KB and 1364 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F, '$2=="/pay" {print $3, $1}' 压测/qps.txt | sort -k1,1nr -k2,2 | head -1` -> 01:34:24
        then `awk -F, '$2=="/pay"' 压测/qps.txt | wc -l` for the row count asked in the prompt (509)
Turn 2: bash: `awk -F, '$2=="/order" {print $3, $1}' 压测/qps.txt | sort -k1,1nr -k2,2 | head -1` -> 00:31:52
        then `awk -F, '$2=="/order"' 压测/qps.txt | wc -l` for the row count asked in the prompt (341)
Final answer: /order 的 qps 峰值出现在 00:31:52，/order 共有 341 条采样。

## Why the answer is unique
接口 is a whole-value column; the peak is shared by several rows and the README picks the earliest time. The README (压测/说明.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. /order 接口峰值 qps 对应的时间是多少？并列取最早。
2. 接口恰好是 /order 的记录里，qps 最高的是哪个时刻？
3. 按说明.md，/order 的 qps 最大值出现在什么时间？
4. qps.txt 中 /order（不含 /order/list）峰值那一刻的时间。
5. 找出 /order 的峰值 qps，若并列取最早，告诉我时间。
