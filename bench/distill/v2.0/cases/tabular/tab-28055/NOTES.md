## Traps
- None. Turn 1 asks the assistant to wait for the two student names.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two students should I total?"
Turn 2: read tutoring/billing/2026-09.csv, sum the fee column over every row of Maya Chen and Liam Ortiz: 595 dollars. Final answer in one sentence with both names and the total. Criteria: turn 1 zero-call and asks which students; turn 2 contains 595.

## Changelog
- v2：反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。

## Why the answer is unique
Turn 2 fixes the two students; their fee rows sum to a single value, and the other students' rows are out of scope.
