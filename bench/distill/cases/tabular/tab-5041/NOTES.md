## Traps
- None. Both weights sit on the same row and the question fixes which one is larger: the declared weight at filling against the graded weight after maturing.

## Reference solution
1. List the workspace: the July grading file and a short readme.
2. Read vat_grading_2026-07.csv, add the declared_kg column and the graded_kg column separately, and take the declared total less the graded total: 67.6 kilograms.

## Why the answer is unique
The readme states one row per vat and names declared_kg as the weight at filling and graded_kg as the weight at grading, so the shortfall per vat is declared_kg less graded_kg, and the shortfall across the month is the difference of the two column totals. Every graded_kg is smaller than its own declared_kg, so no vat contributes a negative shortfall and there is no reading in which the difference runs the other way. The difference is 67.6 kilograms.
