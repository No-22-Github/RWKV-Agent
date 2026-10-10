## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `采样间隔秒: 30   # 2026-07 校准后调整` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 雨量站/采集.yaml; locate the target line `采样间隔秒: 30   # 2026-07 校准后调整`.
3. replace_lines that single line with `采样间隔秒: 20   # 2026-07 校准后调整` (only 30 -> 20).
4. Read 雨量站/采集.yaml back and confirm only that line changed.
Final answer: '已把 雨量站/采集.yaml 里的 采样间隔秒 改成 20，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
