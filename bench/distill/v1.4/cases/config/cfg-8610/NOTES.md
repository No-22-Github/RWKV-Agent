## Traps
- TR-DECOY: 一号厅有一行完全相同的内容，只能改三号厅。 Target line: `    每日最大场次: 8   # 含午夜场` (  三号厅:).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 排片/厅配置.yaml; locate the target line `    每日最大场次: 8   # 含午夜场`.
3. replace_lines that single line with `    每日最大场次: 6   # 含午夜场` (only 8 -> 6).
4. Read 排片/厅配置.yaml back and confirm only that line changed.
Final answer: '已把 排片/厅配置.yaml 里的 每日最大场次 改成 6，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
