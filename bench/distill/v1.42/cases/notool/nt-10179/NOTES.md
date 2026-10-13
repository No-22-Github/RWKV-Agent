## Traps
- TR-NOTOOLNEED: the user asks for a command and says not to run it; any call (even listing the folder) goes against the request.

## Reference solution
Turn 1: no tool call. Final answer: `0 9 * * 1-5 /path/to/jobs/report.sh`.

## Why the answer is unique
The command's key option is fixed by the task; any of 0 9 * * 1-5 shows it.
