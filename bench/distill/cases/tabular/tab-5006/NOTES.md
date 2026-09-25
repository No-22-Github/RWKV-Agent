## Traps
- None. One weighed crate per row, so the divisor is simply the number of rows.

## Reference solution
1. List the workspace: one intake log and a short readme.
2. Read crate_intake.csv, add the weight_kg column: 8.4 + 12.55 + 19.2 + 7.85 + 14.3 + 22.6 + 9.15 + 16.4 + 11.25 + 5.9 + 18.75 + 13.05 + 10.6 + 21.35 + 6.45 + 15.8 = 213.6.
3. 213.6 / 16 = 13.35.

## Why the answer is unique
The readme states one row per weighed crate, so every row contributes exactly one crate and the divisor is the row
count of 16. No crate is weighed twice and there is no subtotal line, so the mean is 13.35 and no other reading
of the file gives a different figure.
