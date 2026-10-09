## Traps
- TR-MULTISRC: 12 daily files under 日志/2026-09/; any single file gives a plausible partial count.
- TR-DECOY: 「支付网关超时」 contains the substring 支付超时 but 日志/说明.md says it is the upstream gateway, not ours; a substring grep over-counts.

## Reference solution
1. bash: `cat 日志/2026-09/*.csv | awk -F, '$4=="支付超时"' | wc -l` (exact field match, not substring).
Final answer: 九月一共 101 次支付超时（按事件列精确等于「支付超时」统计，网关超时不算）。

## Why the answer is unique
The decoy is excluded by the field rule written in 日志/说明.md; counting by exact field over all 12 files gives one number.
