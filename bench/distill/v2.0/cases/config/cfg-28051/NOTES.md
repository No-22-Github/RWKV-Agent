## Traps
- None. Turn 1 asks the assistant to wait for the room names.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two rooms should I look up?"
Turn 2: read config/rooms/maple.yaml and config/rooms/willow.yaml: capacity 12 and 8. Final answer in one sentence: Maple caps at 12 children and Willow at 8. Criteria: turn 1 zero-call and asks which rooms; turn 2 contains 12 and 8 as whole tokens.

## Changelog
- v2：反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。

## Why the answer is unique
Each room file sets capacity explicitly, so the values are 12 (Maple) and 8 (Willow); Cedar is out of scope.
