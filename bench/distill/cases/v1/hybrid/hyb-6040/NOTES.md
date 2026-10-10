## Traps
- TR-DATEFMT: start_date mixes three styles. BK-2204 (06/07/2026) is 6 July and BK-2206 (09/07/2026) is 9 July under the day/month convention; reading the slashed entries month-first drops both out of the 6-12 July window and returns 3.

## Reference solution
1. Turn 1: list_files to find the bookings file.
2. read README.md: slashed dates are day/month/year, dotted-length ISO is year-month-day, and the spelled form is written out; nothing is month-first.
3. read bookings/july-2026.csv, normalise every start date, and count those inside 6-12 July: BK-2204, BK-2205, BK-2206, BK-2207, BK-2208 = 5.
4. Turn 2 needs no further call: the same normalised list gives 4 starts inside 20-26 July (BK-2211, BK-2212, BK-2213, BK-2214).

## Why the answer is unique
The README pins the convention, so each entry has exactly one date: 06/07/2026 is 6 July, not 6 June, and 09/07/2026 is 9 July, not 9 September. With that settled, the 6-12 July window holds exactly five starts and the 20-26 July window four; the month-first reading is the only way to reach 3, and it contradicts the file's own note. No booking starts on a window edge in another style, so no second count is defensible.

## Five alternative phrasings of the task
1. trewarren cottages bookings first july week
2. how many bookings started 6 to 12 july
3. trewarren july letting summary
4. bookings starting 20 to 26 july trewarren
5. trewarren cottages july start dates
