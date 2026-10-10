## Traps
- None declared. The scoring run adds a second monthly file the model never saw (expect.run.hidden_files, kept inside pressings/), so a --total line computed from September's rows alone prints 510 instead of the merged 720.

## Reference solution
1. Read press.py: the totals and their order are already right.
2. Read pressings/2026-09.csv to confirm the columns.
3. Add the --total flag: with it print only the GRAND line over every pressings/*.csv; without it keep today's behavior exactly.

## Why the answer is unique
The grand total is fixed by the merged exports: 720 bottles once the scoring run's pressings/2026-10.csv is in, so the flag's output is the single line GRAND,720. A flag that keeps printing the per-variety lines, or a total summed over September alone (510), differs from the expected stdout, and the prompt pins that the no-flag behavior stays byte-identical.
