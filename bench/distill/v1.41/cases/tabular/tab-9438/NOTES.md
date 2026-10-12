## Traps
- TR-DECOY: exact answer 283; the loose reading (internal notes included, the longest line is internal) gives 242.
- TR-TRUNC: the file is 129KB and 1196 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="comment" {print length($0), NR}' support/tickets.txt | sort -rn | head -1` -> 283
Final answer: The longest comment is on line 283.

## Why the answer is unique
kind is a whole-value column; the longest comment line is strictly longer than every other comment. The README (support/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Which line of tickets.txt is the longest comment?
2. Among rows of kind comment, which line has the most characters?
3. Per support/README.md, give the line number of the longest customer-visible note.
4. Internal notes excluded, find the longest comment line and report its line number.
5. Line number of the longest line whose kind is comment.
