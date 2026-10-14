## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `find 临时 -name '*.tmp' -mtime +7 -delete`（先去掉 -delete 预览一遍）。

## Why the answer is unique
The command's key option is fixed by the task; any of -mtime +7 shows it.
