## Traps
- TR-DECOY: 记录里还有已否决的停止阈值 7.0，不能写进去。 Target line: `  启动溶氧阈值: 4.5    # mg/L，低于即启动` ((no section needed)).

## Reference solution
1. 读 鱼塘/农技员记录.txt 取得新值 5.0
2. Read 鱼塘/增氧机.yaml; locate the target line `  启动溶氧阈值: 4.5    # mg/L，低于即启动`.
3. replace_lines that single line with `  启动溶氧阈值: 5.0    # mg/L，低于即启动` (only 4.5 -> 5.0).
4. Read 鱼塘/增氧机.yaml back and confirm only that line changed.
Final answer: '已把 鱼塘/增氧机.yaml 里的 启动溶氧阈值 改成 5.0，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
