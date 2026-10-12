## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or even listing the directory, breaks the request.

## Reference solution
No tool call. Final answer: `sed -i 's/^env: staging$/env: production/' app/config/*.yml`, with a note to review (or try without -i) before running.

## Why the answer is unique
The user said not to execute; any tool call violates the request.

## Five alternative phrasings of the task
1. Give me a sed one-liner that switches env: staging to env: production in app/config/*.yml. Do not execute anything.
2. What sed command would replace staging with production on the env line of the yml files in app/config? Just tell me, I'll run it myself.
3. Draft the command for changing the env value in app/config yml files from staging to production; no running it, please.
4. I need a command (not executed) that rewrites 'env: staging' to 'env: production' across app/config.
5. Show me how to do the staging-to-production env swap in app/config/*.yml with sed. Don't touch the files.
