## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `  温度: 85       # 80g 纸对应 ℃` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 车间/烘干线.yaml; locate the target line `  温度: 85       # 80g 纸对应 ℃`.
3. replace_lines that single line with `  温度: 82       # 80g 纸对应 ℃` (only 85 -> 82).
4. Read 车间/烘干线.yaml back and confirm only that line changed.
Final answer: '已把 车间/烘干线.yaml 里的 温度 改成 82，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
