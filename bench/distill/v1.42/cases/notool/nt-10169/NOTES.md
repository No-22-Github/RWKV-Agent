## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `find 素材 -type f -size +100M`。

## Why the answer is unique
The command's key option is fixed by the task; any of -size +100M, -size +100m, -size +102400k shows it.
