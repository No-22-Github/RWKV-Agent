## Traps
- TR-DECOY: [月考] 段有一模一样的及格线行。 Target line: `及格线 = 60     ; 满分 100` ([模拟卷]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 教务/测验.ini; locate the target line `及格线 = 60     ; 满分 100`.
3. replace_lines that single line with `及格线 = 65     ; 满分 100` (only 60 -> 65).
4. Read 教务/测验.ini back and confirm only that line changed.
Final answer: '已把 教务/测验.ini 里的 及格线 改成 65，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
