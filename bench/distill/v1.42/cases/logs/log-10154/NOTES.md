## Traps
- TR-DECOY: the root last_run.log says 0. Every bash call starts at the workspace root, so a turn-2 `cat last_run.log` after turn 1's `cd jobs/nightly` reads the root copy.

## Reference solution
Turn 1: bash `cd jobs/nightly && ls` -> lists cron.txt among others.
Turn 2: read jobs/nightly/last_run.log by its full path (read tool or bash) -> 137.
Final answer turn 2: The nightly job's last run failed with exit 137 (jobs/nightly/last_run.log; the root file shows exit 0).

## Why the answer is unique
The question is about the file inside jobs/nightly.
