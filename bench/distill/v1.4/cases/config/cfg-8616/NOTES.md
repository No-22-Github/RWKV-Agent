## Traps
- TR-DECOY: 音乐启蒙的试听名额与感统训练原值相同，只能改感统训练。 Target line: `    试听名额: 6` (  感统训练:).

## Reference solution
1. 读 早教/排课单.txt 取得新值 8
2. Read 早教/课程.yaml; locate the target line `    试听名额: 6`.
3. replace_lines that single line with `    试听名额: 8` (only 6 -> 8).
4. Read 早教/课程.yaml back and confirm only that line changed.
Final answer: '已把 早教/课程.yaml 里的 试听名额 改成 8，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
