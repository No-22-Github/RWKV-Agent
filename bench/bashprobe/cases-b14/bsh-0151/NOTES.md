## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `sort -t, -k3,3nr 数据.csv`。

## Why the answer is unique
The command's key option is fixed by the task; any of -k3, -k 3, -k3,3 shows it.
