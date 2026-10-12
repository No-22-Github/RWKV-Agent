## Traps
- TR-MULTISRC: six per-room alert tables; the first room alone gives 25.
- TR-DECOY: 「磁盘使用率高-演练」 and 「磁盘使用率高于预警线」 contain the rule name as a substring; 告警/说明.md says the rule is matched by full name. A substring match gives 264.

## Reference solution
1. bash: `cat 告警/2026-10/*.tsv | awk -F'\t' '$3=="磁盘使用率高" && $4=="P1"' | wc -l`
Final answer: 十月 P1 级别的「磁盘使用率高」告警一共 127 次（规则名完整匹配，演练和另一条规则不算）。

## Why the answer is unique
Rule and level are exact tab-separated fields; the README pins full-name matching; all six files are summed.
