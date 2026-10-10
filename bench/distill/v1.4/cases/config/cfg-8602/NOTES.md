## Traps
- TR-DECOY: [微信] 段有同名键且同值 24，只能改 [短信]。 Target line: `提前提醒小时 = 24   ; 患者反馈太早` ([短信]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 设置/预约提醒.ini; locate the target line `提前提醒小时 = 24   ; 患者反馈太早`.
3. replace_lines that single line with `提前提醒小时 = 12   ; 患者反馈太早` (only 24 -> 12).
4. Read 设置/预约提醒.ini back and confirm only that line changed.
Final answer: '已把 设置/预约提醒.ini 里的 提前提醒小时 改成 12，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
