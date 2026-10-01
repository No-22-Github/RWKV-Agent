## Traps
- TR-DECOY: the extraction log has four batches, but Hive 7 and Hive 5 are
  grade B and stay in the farm-gate bucket; labelling all four is the trap.

## Reference solution
1. Read README.md: only grade A rows become label lines `- <hive> - <frames> frames` in log order, file named after the extraction date.
2. Read sheets/extraction-2026-09-26.txt.
3. Write labels/2026-09-26.txt with the Hive 3 and Hive 1 lines.

## Why the answer is unique
The README sends every grade B batch to the farm-gate bucket, so labelling
Hive 7 or Hive 5 would put ungraded honey into the labelled jars. The two
grade A rows carry their hive names and frame counts verbatim, and the line
shape is fixed by the README, so the list has exactly one content.
