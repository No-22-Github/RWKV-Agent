## Traps
- TR-DECOY: 冷链件段也有「超期天数」键，不能误改。 Target line: `    超期天数: 3        # 超期转退回` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 站点/驿站规则.yaml; locate the target line `    超期天数: 3        # 超期转退回`.
3. replace_lines that single line with `    超期天数: 5        # 超期转退回` (only 3 -> 5).
4. Read 站点/驿站规则.yaml back and confirm only that line changed.
Final answer: '已把 站点/驿站规则.yaml 里的 超期天数 改成 5，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
