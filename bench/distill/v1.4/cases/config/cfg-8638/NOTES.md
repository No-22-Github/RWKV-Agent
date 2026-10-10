## Traps
- TR-DECOY: A 栏同值同注释，不能改。 Target line: `    每次投喂kg: 12.5   # 含补料` (  B栏:).

## Reference solution
1. 读 养殖/兽医意见.txt 取得新值 11.0
2. Read 养殖/饲喂.yaml; locate the target line `    每次投喂kg: 12.5   # 含补料`.
3. replace_lines that single line with `    每次投喂kg: 11.0   # 含补料` (only 12.5 -> 11.0).
4. Read 养殖/饲喂.yaml back and confirm only that line changed.
Final answer: '已把 养殖/饲喂.yaml 里的 每次投喂kg 改成 11.0，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
