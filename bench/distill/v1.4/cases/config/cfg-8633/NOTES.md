## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `  上报周期分钟: 30    # 流蜜期可缩短` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 蜂场/称重.yaml; locate the target line `  上报周期分钟: 30    # 流蜜期可缩短`.
3. replace_lines that single line with `  上报周期分钟: 10    # 流蜜期可缩短` (only 30 -> 10).
4. Read 蜂场/称重.yaml back and confirm only that line changed.
Final answer: '已把 蜂场/称重.yaml 里的 上报周期分钟 改成 10，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
