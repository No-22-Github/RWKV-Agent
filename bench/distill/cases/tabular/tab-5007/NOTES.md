## Traps
- TR-HEADER: meter_export_2026-08.csv ends with a `TOTAL` line carrying the column sum and its own reading_id.
  Treating that line as a reading gives a column sum of twice the report total over 61 readings, so the average
  comes out as 95.03 instead of 48.31.

## Reference solution
1. List the workspace: the billing export and a short readme.
2. Read meter_export_2026-08.csv and note that the last line is a `TOTAL` row, not a reading.
3. Average the 60 reading volumes (sum the volume_m3 column, then divide by the number of readings): 48.31.

## Why the answer is unique
The readme says one row per submitted reading, and the export adds a totals line whose reading_id is `TOTAL`; that
line repeats the sum of the other rows rather than describing a meter, so counting it as a reading both invents a
61st reading and doubles the total. Only the 60 rows that name a meter and a reading date are readings, so the
mean is 48.31.
