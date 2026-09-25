## Traps
- TR-DECOY: the session's gas total sits on the summary line as a large round number of the same size as the wanted total, so reporting that total gives 1837 instead of 2549; the summary carries no garment total, so the loads have to be added up from the cycle lines.

## Reference solution
1. List the workspace: README.md and logs/boiler.log.
2. Read README.md: `load` is the number of garments a cycle took in and the summary line carries the cycle count and the gas units only.
3. Read logs/boiler.log. The cycle lines carry loads of 186, 201, 178, 214, 193, 207, 182, 199, 211, 188, 204, 195, 191 garments, which add up to 2549.

## Why the answer is unique
The question asks for garments taken in, and README.md says `load` is that number, so the 13 cycle lines of the session are the records to add. Their loads total 2549 garments. The decoy 1837 is the session's gas total from the summary line, which is a quantity of fuel, not garments, and reading only the summary cannot produce a garment total at all. With `load` added over the session, the answer is 2549.

## Fixture notes
Every cycle line is on 3 July 2026, the summary line accounts for all 13 cycles, and the loads differ from one another so no line can be taken for another.
