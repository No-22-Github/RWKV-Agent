## Traps
- TR-MISSING: Deck 2 has three unlogged days across the fortnight (an empty cell, a dash and NA). Spreading its 113.8 hours across all 14 days gives 8.13 instead of 9.48.

## Reference solution
1. Turn 1: list_files to find the oven log.
2. read README.md: empty, dash and NA are unlogged days, excluded from averages.
3. read bakery/oven-log-2026.csv and average Deck 2's twelve logged days: 113.8 / 12 = 9.48.
4. Turn 2 needs no further call: the same read shows Deck 3 logged on eleven of the fourteen days, so the count is 11.

## Why the answer is unique
The README fixes the convention: an unlogged day is a day with no entry, and averages run over logged days only. That gives twelve logged days for Deck 2 and eleven for Deck 3. Spreading hours across all fourteen days assumes the ovens idled at zero, which neither the file nor its notes state, and produces 8.13 rather than 9.48. The follow-up's count is the number of Deck 3 rows with an entry, which the same read fixes at 11.

## Five alternative phrasings of the task
1. kneadwell bakery deck 2 average run time
2. how many days did deck 3 log in april
3. kneadwell oven log first fortnight april
4. deck oven hours kneadwell bakery
5. april oven utilisation kneadwell
