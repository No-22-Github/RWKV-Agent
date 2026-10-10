## Traps
- TR-DUPROW: the ticket office wrote three of the 2026 sailings out again, and the repeated rows match their originals in every column. Adding every June 2026 row answers 568 instead of 388.
- TR-HEADER: the log ends with a `TOTAL` line holding the sum of every row in the file, 4554 vehicles, which covers both seasons rather than June 2026.

## Reference solution
1. List the workspace: the sailing log and a short readme.
2. Read README.md: part of the 2026 season was written out twice, so rows can repeat.
3. Read sailings_2025_2026.csv, keep the June 2026 sailings, count each crossing_id once and add the vehicles: 388 vehicles. The last line is a `TOTAL` line with no date and is not a sailing.

## Why the answer is unique
The readme states one row per sailing, says the log holds the 2025 and 2026 seasons and that part of the 2026 season was written out twice; the repeated rows match their originals in every column, so they are the same crossings and counting each crossing_id once is the only reading of the file. The `TOTAL` line names no route or date and sums both seasons, so it cannot stand for June 2026. The June 2026 sailings add up to 388 vehicles.
