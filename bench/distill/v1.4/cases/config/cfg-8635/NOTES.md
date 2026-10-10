## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `下豆温度: 208      # ℃，浅烘` ((no section needed)).

## Reference solution
1. 读 烘豆/备忘.txt 取得新值 210
2. Read 烘豆/曲线.yaml; locate the target line `下豆温度: 208      # ℃，浅烘`.
3. replace_lines that single line with `下豆温度: 210      # ℃，浅烘` (only 208 -> 210).
4. Read 烘豆/曲线.yaml back and confirm only that line changed.
Final answer: '已把 烘豆/曲线.yaml 里的 下豆温度 改成 210，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
