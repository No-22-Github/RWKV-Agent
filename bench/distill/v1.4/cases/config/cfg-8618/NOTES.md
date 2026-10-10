## Traps
- TR-DECOY: A 梯那行文字完全一样，只能改 B 梯。 Target line: `    巡检周期天: 30     # 国标要求不超过 30 天` (  1号楼B梯:).

## Reference solution
1. 读 物业/工单-0925.txt 取得新值 15
2. Read 物业/电梯.yaml; locate the target line `    巡检周期天: 30     # 国标要求不超过 30 天`.
3. replace_lines that single line with `    巡检周期天: 15     # 国标要求不超过 30 天` (only 30 -> 15).
4. Read 物业/电梯.yaml back and confirm only that line changed.
Final answer: '已把 物业/电梯.yaml 里的 巡检周期天 改成 15，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
