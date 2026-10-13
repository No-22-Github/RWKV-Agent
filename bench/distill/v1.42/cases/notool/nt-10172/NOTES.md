## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.
- Turn 2 does ask to run it: now one bash call is right, and the answer is 4.

## Reference solution
Turn 1: no tool call. Final answer: `grep -rn TODO 代码`。
Turn 2: bash `grep -rn TODO 代码 | wc -l` -> 4.

## Why the answer is unique
The command's key option is fixed by the task; any of grep -rn, grep -nr, grep -r -n, grep -n -r, grep -Rn, grep -nR shows it.
