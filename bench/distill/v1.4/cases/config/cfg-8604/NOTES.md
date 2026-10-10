## Traps
- TR-DECOY: 白班同样有「间隔分钟」键，通知只改夜班。 Target line: `    间隔分钟: 45` (  夜班:).

## Reference solution
1. 读 护理/通知-0921.txt 取得新值 30
2. Read 护理/巡房.yaml; locate the target line `    间隔分钟: 45`.
3. replace_lines that single line with `    间隔分钟: 30` (only 45 -> 30).
4. Read 护理/巡房.yaml back and confirm only that line changed.
Final answer: '已把 护理/巡房.yaml 里的 间隔分钟 改成 30，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
