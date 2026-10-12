## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: > truncates/overwrites the file, >> appends to the end; > can destroy existing data.

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['append', 'overwrite', 'truncat', 'replace'].

## Five alternative phrasings of the task
1. What is the difference between > and >> redirection in bash?
2. If I write `cmd > out` versus `cmd >> out`, what happens to existing content?
3. Which redirect overwrites and which appends?
4. Explain shell output redirection with > and >>.
5. Is `>>` safer than `>` for a file I want to keep?
