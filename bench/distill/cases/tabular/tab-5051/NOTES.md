## Traps
- TR-DECOY: the log holds two seasons, and the largest single draw in the file is a 2025 draw of 61.4 tonnes. A reader who takes the largest row of the log answers 61.4 instead of 48.7.
- TR-HEADER: the log ends with a `TOTAL` line holding the season figures for the whole file, 1789.9 tonnes, which is a total rather than a draw.

## Reference solution
1. List the workspace: the draw log and a short readme.
2. Read kiln_draws_2025_2026.csv and keep the rows whose draw_date falls in 2026; the last line is a `TOTAL` line with no date and is not a draw.
3. Take the largest tonnes among the 2026 draws: 48.7 tonnes.

## Why the answer is unique
The readme says one row per draw and that the log holds the 2025 and 2026 seasons, so a draw of the 2026 season is a row dated 2026 and the 2025 rows cannot supply the figure even though the largest of them is bigger. The `TOTAL` line names no kiln or date and its figure is the sum of every row, so it stands for two seasons rather than one draw. The largest 2026 row is 48.7 tonnes.
