## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `  课时分钟: 40      # 2025 秋季学期起` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 校务/作息.yaml; locate the target line `  课时分钟: 40      # 2025 秋季学期起`.
3. replace_lines that single line with `  课时分钟: 35      # 2025 秋季学期起` (only 40 -> 35).
4. Read 校务/作息.yaml back and confirm only that line changed.
Final answer: '已把 校务/作息.yaml 里的 课时分钟 改成 35，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
