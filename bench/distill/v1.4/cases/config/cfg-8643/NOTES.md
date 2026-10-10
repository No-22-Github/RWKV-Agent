## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `idle_timeout_min = 15   # compliance: <= 15` ((no section needed)).

## Reference solution
1. Read bastion/SEC-209.txt: new value 10
2. Read bastion/session.toml; locate the target line `idle_timeout_min = 15   # compliance: <= 15`.
3. replace_lines that single line with `idle_timeout_min = 10   # compliance: <= 15` (only 15 -> 10).
4. Read bastion/session.toml back and confirm only that line changed.
Final answer: 'Updated bastion/session.toml: the value is now 10, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
