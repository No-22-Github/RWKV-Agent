## Traps
- None. The rate is stated in the request and one column carries every distance the payment needs.

## Reference solution
1. List the workspace: the August night service log and a short readme.
2. Read night_service_log_2026-08.csv and add night_km: 331.2 kilometres.
3. 331.2 x 1.35 = 447.12, so the supplement owed is 447.12 pounds.

## Why the answer is unique
Each trip has one distance, and the supplement is a fixed payment per kilometre for night service, so the amount
owed is the sum of the night_km column multiplied by the stated rate. No row is a repeat and every row in the log
is a night service, so 447.12 is the only figure the request supports.
