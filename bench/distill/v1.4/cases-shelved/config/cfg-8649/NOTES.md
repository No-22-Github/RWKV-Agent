## Traps
- TR-DECOY: 留言里提到的停止湿度 65% 只是设想，不能写入。 Target line: `  启动土壤湿度: 35    # %，低于即灌` ((no section needed)).

## Reference solution
1. 读 农场/技术员留言.txt 取得新值 40
2. Read 农场/灌溉.yaml; locate the target line `  启动土壤湿度: 35    # %，低于即灌`.
3. replace_lines that single line with `  启动土壤湿度: 40    # %，低于即灌` (only 35 -> 40).
4. Read 农场/灌溉.yaml back and confirm only that line changed.
Final answer: '已把 农场/灌溉.yaml 里的 启动土壤湿度 改成 40，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
