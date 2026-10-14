## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `for f in notes/*.txt; do mv "$f" "${f%.txt}.md"; done`.

## Why the answer is unique
The command's key option is fixed by the task; any of mv shows it.
