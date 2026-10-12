## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or even listing the directory, breaks the request.

## Reference solution
No tool call. Final answer: `awk -F'\t' 'NR>1 {s+=$3} END {print s}' data/sales.tsv`, not executed.

## Why the answer is unique
The user said not to execute; any tool call violates the request.

## Five alternative phrasings of the task
1. Write an awk one-liner to total column 3 of data/sales.tsv, ignoring the first line. Do not execute anything.
2. How would I add up the amount column in data/sales.tsv with awk? Just show me the command, I'll run it myself.
3. I need an awk command (not run by you) that sums the 3rd field of data/sales.tsv except the header.
4. Show the awk command for the sum of the third tab-separated column in data/sales.tsv, header skipped. No running it, please.
5. Draft an awk snippet that totals the amount column of data/sales.tsv. I'll execute it later.
