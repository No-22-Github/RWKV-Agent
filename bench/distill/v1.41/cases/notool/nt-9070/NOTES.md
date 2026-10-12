## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `grep -c ERROR 日志/*.log`，每个文件输出一行「文件名:匹配行数」。

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.
