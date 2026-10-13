## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `sed -i 's/旧品牌/新品牌/g' 文案/*.md`（建议先 `grep -rn 旧品牌 文案` 看命中）。

## Why the answer is unique
The command's key option is fixed by the task; any of sed -i shows it.
