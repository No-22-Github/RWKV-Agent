## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `同步间隔分钟: 15      # 2026-06 与平台对账后调整` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 配置/房态同步.yaml; locate the target line `同步间隔分钟: 15      # 2026-06 与平台对账后调整`.
3. replace_lines that single line with `同步间隔分钟: 10      # 2026-06 与平台对账后调整` (only 15 -> 10).
4. Read 配置/房态同步.yaml back and confirm only that line changed.
Final answer: '已把 配置/房态同步.yaml 里的 同步间隔分钟 改成 10，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
