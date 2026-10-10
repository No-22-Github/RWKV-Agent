## Traps
- TR-DECOY: 「开启温度滞后」键名以「开启温度」开头，不能改错行。 Target line: `开启温度 = 28      # ℃` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 大棚/卷帘.toml; locate the target line `开启温度 = 28      # ℃`.
3. replace_lines that single line with `开启温度 = 26      # ℃` (only 28 -> 26).
4. Read 大棚/卷帘.toml back and confirm only that line changed.
Final answer: '已把 大棚/卷帘.toml 里的 开启温度 改成 26，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
