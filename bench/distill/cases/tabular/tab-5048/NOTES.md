## Traps
- TR-DEFN: the mill scale weighs paper and wrapping together, so the conspicuous figure in the log is the gross weight. The invoice is for the paper alone, which is gross_tonnes less wrap_tonnes on every row. A reader who adds the gross column answers 546.0 instead of 524.4.

## Reference solution
1. List the workspace: the July production file and a short readme.
2. Read production_2026-07.csv and, for each row, take gross_tonnes less wrap_tonnes.
3. Add those fifty figures: 524.4 tonnes.

## Why the answer is unique
The readme states one row per batch, gross_tonnes as the weight on the mill scale and wrap_tonnes as the weight of the wrapping on the reel, so the paper on a row is the scale weight less the wrapping weight. Nothing in the workspace weights the paper alone, and a row's paper weight cannot exceed its scale weight, so the invoiced weight is the sum of the differences: 524.4 tonnes.
