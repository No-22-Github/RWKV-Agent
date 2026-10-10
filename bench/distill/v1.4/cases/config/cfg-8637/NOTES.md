## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `MIN_DEPTH_CM=120     # 低于则停航` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 渡口/运行.env; locate the target line `MIN_DEPTH_CM=120     # 低于则停航`.
3. replace_lines that single line with `MIN_DEPTH_CM=140     # 低于则停航` (only 120 -> 140).
4. Read 渡口/运行.env back and confirm only that line changed.
Final answer: '已把 渡口/运行.env 里的 MIN_DEPTH_CM 改成 140，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
