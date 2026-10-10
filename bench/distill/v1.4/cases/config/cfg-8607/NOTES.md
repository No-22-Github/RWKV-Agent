## Traps
- TR-DECOY: [夜间] 段有完全相同的一行，只能改 [白天]。 Target line: `每小时 = 6      # 单位 元` ([白天]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 停车场/费率.toml; locate the target line `每小时 = 6      # 单位 元`.
3. replace_lines that single line with `每小时 = 8      # 单位 元` (only 6 -> 8).
4. Read 停车场/费率.toml back and confirm only that line changed.
Final answer: '已把 停车场/费率.toml 里的 每小时 改成 8，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
