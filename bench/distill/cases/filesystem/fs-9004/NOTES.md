## Traps
None beyond the date rule: the issue month is in the file name (9 invoices fall in January-June).

## Reference solution
1. bash: `for f in inbox/inv-2026-0[1-6]-*.pdf; do mv "$f" archive/2026H1/; done`
2. bash: `ls inbox archive/2026H1` to confirm.
Final answer: moved the 9 invoices dated January to June 2026 into archive/2026H1/; the later ones and notes.txt stay in inbox/.

## Why the answer is unique
The month field of each name decides membership; nothing else moves.
