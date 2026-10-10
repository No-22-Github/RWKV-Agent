## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `功率上限kW = 120  # 变压器限制` ((no section needed)).

## Reference solution
1. 读 充电站/来函摘要.txt 取得新值 90
2. Read 充电站/站点-07.toml; locate the target line `功率上限kW = 120  # 变压器限制`.
3. replace_lines that single line with `功率上限kW = 90  # 变压器限制` (only 120 -> 90).
4. Read 充电站/站点-07.toml back and confirm only that line changed.
Final answer: '已把 充电站/站点-07.toml 里的 功率上限kW 改成 90，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
