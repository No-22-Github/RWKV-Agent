## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `tick_rate = 64     ; Hz` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read server/game.ini; locate the target line `tick_rate = 64     ; Hz`.
3. replace_lines that single line with `tick_rate = 32     ; Hz` (only 64 -> 32).
4. Read server/game.ini back and confirm only that line changed.
Final answer: 'Updated server/game.ini: the value is now 32, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
