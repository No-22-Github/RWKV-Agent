## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `有效分钟 = 30     ; 过期需重新生成` ((no section needed)).

## Reference solution
1. 读 园务/工单-117.md 取得新值 20
2. Read 园务/接送.ini; locate the target line `有效分钟 = 30     ; 过期需重新生成`.
3. replace_lines that single line with `有效分钟 = 20     ; 过期需重新生成` (only 30 -> 20).
4. Read 园务/接送.ini back and confirm only that line changed.
Final answer: '已把 园务/接送.ini 里的 有效分钟 改成 20，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
