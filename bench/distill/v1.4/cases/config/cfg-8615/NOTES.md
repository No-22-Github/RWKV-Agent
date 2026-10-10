## Traps
- TR-DECOY: 柳岸花园段的保留天数同值同注释，不能改。 Target line: `保留天数 = 2     ; 超期退回团长` ([自提点-紫荆苑]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 团购/自提点.ini; locate the target line `保留天数 = 2     ; 超期退回团长`.
3. replace_lines that single line with `保留天数 = 3     ; 超期退回团长` (only 2 -> 3).
4. Read 团购/自提点.ini back and confirm only that line changed.
Final answer: '已把 团购/自提点.ini 里的 保留天数 改成 3，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
