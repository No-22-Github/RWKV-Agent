## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `发车时间: "06:50"   # 冬令时` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 校车/路线三.yaml; locate the target line `发车时间: "06:50"   # 冬令时`.
3. replace_lines that single line with `发车时间: "07:05"   # 冬令时` (only 06:50 -> 07:05).
4. Read 校车/路线三.yaml back and confirm only that line changed.
Final answer: '已把 校车/路线三.yaml 里的 发车时间 改成 07:05，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
