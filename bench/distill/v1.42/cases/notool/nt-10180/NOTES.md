## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `grep -rn TODO web --exclude-dir=node_modules`.

## Why the answer is unique
The command's key option is fixed by the task; any of --exclude-dir, -not -path, ! -path, -prune shows it.
