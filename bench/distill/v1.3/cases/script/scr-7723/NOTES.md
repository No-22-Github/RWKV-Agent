## Traps
- TR-MISSING: the frames column mixes two empty shapes (an empty cell on 09-12 and a dash on 09-26, both for Foxglove Stack). The buggy script turns both into 0 and still prints Foxglove Stack,0, though the docstring says an unopened hive counts nothing and gets no line. (No hive ever pulls zero frames, so a digit cell is always a real count.)

## Reference solution
1. Read harvest.py: the docstring says unopened hives get no line.
2. Read hives/2026-09.csv: Foxglove Stack's two visits are empty and dashed.
3. Read README.md: empty or dashed means not opened.
4. Fix harvest.py so empty and dashed cells contribute nothing and their hives get no line.

## Why the answer is unique
Skipping empty and dashed cells, the merged run (the scoring run adds hives/2026-10.csv with a dashed Copper Rise visit and a real Foxglove Stack count) prints exactly Bell Thorn,54 / Copper Rise,24 / Foxglove Stack,10 and TOTAL,88. The docstring states that unopened hives count nothing and get no line, so the zero line is the reading the record itself rules out; a fix that drops the whole hive rather than the single unopened visit would lose October's 10 frames and differ from the expected stdout.
