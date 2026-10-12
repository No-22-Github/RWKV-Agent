## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or even listing the directory, breaks the request.

## Reference solution
No tool call. Final answer: `tar -czf reports.tar.gz --exclude='reports/tmp' reports`, not executed.

## Why the answer is unique
The user said not to execute; any tool call violates the request.

## Five alternative phrasings of the task
1. Write the tar command that compresses reports into reports.tar.gz but skips reports/tmp. Do not run it.
2. I want a gzip tarball of the reports folder without the tmp subfolder. Give me the command; I'll run it.
3. Show me how to create reports.tar.gz from reports, excluding reports/tmp. No execution please.
4. Which tar invocation archives reports (minus reports/tmp) into a .tar.gz? Command only, nothing run.
5. Draft a tar command for reports.tar.gz that leaves out reports/tmp; I will run it on my side.
