## Traps
- TR-SIGN: refunds stored as positive amounts in refunds.csv; subtracting them as if negative gives 17206.90, adding them as if refunds were income gives the decoy 17206.80.
## Reference solution
1. list_files (1)
2. read_file orders.csv + refunds.csv (2)
3. calculator: 1129.90 + 15947.00 - 129.90 (3)
## Why the answer is unique
Only one refunds row; dates all in August; README defines the refund semantics.
