## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `find src -name '*.py' -print0 | xargs -0 cat | wc -l`，或 `cat src/*.py | wc -l`。

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.
