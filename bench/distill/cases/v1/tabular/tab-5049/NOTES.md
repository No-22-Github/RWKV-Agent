## Traps
- TR-DECOY: splitting_runs_2026-08.csv carries the runs of the Trefriw yard beside the Penrhyddn runs; the Trefriw rows are the larger part of the file, so a reader who counts the export answers 56 instead of the 21 runs of the Penrhyddn yard.

## Reference solution
1. List the workspace: the August run export and a short readme.
2. Read splitting_runs_2026-08.csv and note that the yard column separates the two yards the export covers.
3. Count the rows whose yard is Penrhyddn: 21 splitting runs.

## Why the answer is unique
The readme says one row per splitting run and that the export covers both yards, so the yard column decides which runs belong to Penrhyddn. Every Trefriw row names the other yard, and no run is recorded twice, so the Penrhyddn rows are exactly the yard's runs: 21.
