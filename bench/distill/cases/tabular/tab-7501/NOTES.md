## Traps
- TR-DECOY: data/rentals_log.csv carries the near-name class "Sunset Paddle Plus" beside the target "Sunset Paddle". Summing the Plus rows (or both classes) gives 1570.07. June and August rows are further distractors around the July target.

## Reference solution
1. data_query: {"path":"data/rentals_log.csv","filter":{"rental_month":"2026-07","rental_class":"Sunset Paddle"},"operation":"sum","field":"revenue"} -> 1962.67.
2. Reply with the number 1962.67 only.

## Why the answer is unique
The decoy 1570.07 is the Sunset Paddle Plus total, but the task names the Sunset Paddle class, and the README fixes the naming: Sunset Paddle is the standard guided loop, Plus is a separate class. Every row carries exactly one class, so no reading mixes them. Rows dated June or August fail the month condition. The answer is 1962.67.
