## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `daily = 14     # days` ((no section needed)).

## Reference solution
1. Read ops/runbook-note.md: new value 21
2. Read ops/backup.toml; locate the target line `daily = 14     # days`.
3. replace_lines that single line with `daily = 21     # days` (only 14 -> 21).
4. Read ops/backup.toml back and confirm only that line changed.
Final answer: 'Updated ops/backup.toml: the value is now 21, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
