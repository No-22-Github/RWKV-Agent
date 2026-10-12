## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory or file but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `find data -type f -exec du -k {} + | sort -rn | head -10`, or `ls -lSR data | head`.

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.

## Alternative phrasings
1. Give me a one-liner for the ten biggest files in ./data, but don't execute it.
2. How would I list the largest 10 files below data/? Only the command please, I'll run it.
3. Which command shows the top 10 files by size inside ./data? No need to run it.
4. I want the 10 biggest files under data; write the command, don't run it.
5. Write a shell command for the 10 largest files in ./data. I'll run it myself later.
