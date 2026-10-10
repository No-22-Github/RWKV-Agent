## Traps
- None. Every line in the journal is one completed cycle and names the vat it drew from, so counting the V-3 lines is the whole task.

## Reference solution
1. List the workspace: README.md and logs/vat-cycle.log.
2. Read logs/vat-cycle.log and count the lines whose `vat` is V-3: the file holds 20 cycles, 12 of them on vat V-3.

## Why the answer is unique
README.md says each machine is named after the vat it draws from and writes one line per cycle it completes, and the journal is replaced at the start of the next day's shift, so the 20 lines are exactly the cycles of 15 September 2026. Twelve of them carry vat=V-3; the V-1 and V-5 cycles belong to the other two machines and cannot be counted as V-3 cycles. The `minutes` column is each cycle's running time, so totalising it answers a different question.

## Fixture notes
Every line carries a UTC stamp on 15 September 2026, the three machines are interleaved through the day, and V-3 runs more cycles than either of the others. The `minutes` and `metres` values are each cycle's running time and fabric length, and no line and no stamp carries the number that answers the question.
