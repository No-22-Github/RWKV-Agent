## Traps
- TR-DECOY: 入住时间一行同属时间字段，不能改。 Target line: `  退房时间: "12:00"   # 2025 起统一` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 前台/客房规则.yaml; locate the target line `  退房时间: "12:00"   # 2025 起统一`.
3. replace_lines that single line with `  退房时间: "11:30"   # 2025 起统一` (only 12:00 -> 11:30).
4. Read 前台/客房规则.yaml back and confirm only that line changed.
Final answer: '已把 前台/客房规则.yaml 里的 退房时间 改成 11:30，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
