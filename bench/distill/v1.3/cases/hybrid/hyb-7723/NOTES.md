## Traps
- TR-DECOY: logs/energy-2026-09.csv carries the look-alike meter M-13 (三号库房) beside the
  workshop meters M-3A/M-3B. Sweeping it into the workshop total gives 13650 instead of 9840.

## Reference solution
1. read_file README.md, then docs/line-map.md: the workshop meters are M-3A and M-3B; M-13 belongs to the storehouse.
2. read_file logs/energy-2026-09.csv. Turn 1: M-3A + M-3B sum to 9840 度. Turn 2: dropping 14-16 September removes 173 + 262, giving 9405 度.
3. Turn 3: after the exclusion M-3B (5468) leads M-3A (3937). Turn 4: M-3B's kept total is 5468 度.

## Why the answer is unique
M-13's number starts with the same digit and its readings sit in the same range, but the line map assigns it to the storehouse, so the workshop total is 9840 and only that. The three maintenance days carry exactly 173 (M-3A) and 262 (M-3B) 度, all of them workshop rows, so the corrected total is 9405 and M-3B's share 5468; no other grouping fits the line map.

## Five alternative phrasings of the task
1. yunshan electric september meter readings
2. workshop three energy total for september
3. total excluding the maintenance shutdown days
4. which meter led after the exclusion
5. september energy by meter and workshop
