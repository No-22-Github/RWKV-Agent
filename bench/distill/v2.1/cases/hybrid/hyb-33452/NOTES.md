## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
三处 debug→info；用户要求 pay 恢复 debug。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 三个服务的日志级别都从 debug 降到 info。
2. 麻烦问下：三个服务的日志级别都从 debug 降到 info。
3. 三个服务的日志级别都从 debug 降到 info。（简单说就行）
4. 你好，三个服务的日志级别都从 debug 降到 info。
5. 还有件事：三个服务的日志级别都从 debug 降到 info。
