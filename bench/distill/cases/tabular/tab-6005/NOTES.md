## Traps
- TR-MISSING: the units_output column mixes plain counts with NA, a dash and empty cells. Four
  Line 2 rows carry no figure; a reader who divides the Line 2 total by all 14 Line 2 days gets
  5644.07 instead of the average over the 10 recorded figures, 7901.7.

## Reference solution
1. List the workspace: the May output log and a readme.
2. Read README.md: only days with a figure count toward averages.
3. Read output/line_output_2026-05.csv, keep the 10 Line 2 rows that carry a count, and take the
   mean: 7901.7.

## Why the answer is unique
The readme defines every non-numeric marker as a day with no usable figure and states that only
days with a figure count toward averages, so the denominator is fixed at the 10 recorded Line 2
days. Treating the four unrecorded days as zero output is the decoy 5644.07 and contradicts the
readme: a maintenance day or an unsynced counter is not a day at zero. The answer is 7901.7.
