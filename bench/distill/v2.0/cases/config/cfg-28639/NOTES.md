## Traps
- TR-DECOY: 「锁定分钟上限」键名以「锁定分钟」开头，不能改错行。 Target line: `锁定分钟 = 15       # 连续输错密码后` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 快递柜/格口.toml; locate the target line `锁定分钟 = 15       # 连续输错密码后`.
3. replace_lines that single line with `锁定分钟 = 10       # 连续输错密码后` (only 15 -> 10).
4. Read 快递柜/格口.toml back and confirm only that line changed.
Final answer: '已把 快递柜/格口.toml 里的 锁定分钟 改成 10，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
