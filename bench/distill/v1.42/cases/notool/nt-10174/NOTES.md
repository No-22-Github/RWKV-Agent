## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.
- Turn 2 does ask to run it: now one bash call is right, and the answer is app-12.bin.

## Reference solution
Turn 1: no tool call. Final answer: `find build -type f -exec ls -s {} + | sort -rn | head -10` (or `du -a build | sort -rn | head -n 10`).
Turn 2: bash `find build -type f -exec ls -l {} + | sort -k5 -rn | head -1` -> app-12.bin.

## Why the answer is unique
The command's key option is fixed by the task; any of head -10, head -n 10, head -n10 shows it.
