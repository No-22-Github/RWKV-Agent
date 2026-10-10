## Traps
- None. Turn 1 asks the assistant to wait for the subject choice.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which subjects' handout folders should I count?"
Turn 2: list tutoring/handouts/math/ and tutoring/handouts/writing/: math has 3 handout files and writing has 2. Final answer in one sentence. Criteria: turn 1 zero-call and asks which subjects; turn 2 contains 3 and 2 as whole tokens.

## Changelog
- v2：反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。

## Why the answer is unique
Turn 2 fixes the two folders; the file counts are 3 (math) and 2 (writing), and every handout file has a distinct non-empty name.
