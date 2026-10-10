## Traps
- None. No trap tag is set: the layout is stated in the script itself, and the fault is a single
  line that joins whole numbers into the printed rows.

## Reference solution
1. Read beaters.py: its module notes name the beats/ directory with one file per month, the
   columns and the printed layout, while the row is built with whole numbers in the join (call 1).
2. Render the two counts as text in the row, leaving the layout and the beats/ sheets as they
   are (call 2).

## Why the answer is unique
The beater sheet prints one line per beat in run_date order, then the totals line:

    2026-09-02,Beater A,9,1240
    2026-09-05,Beater B,14,1875
    2026-09-11,Beater A,11,1495
    2026-09-18,Beater B,7,960
    2026-10-03,Beater A,12,1620
    2026-10-14,Beater B,8,1105
    TOTAL,61,8295

A repair that drops the counts from the row contradicts the layout the machine hall has always
had, and a repair that reads only the September sheet leaves out the later beats. The answer
is 61 reels and 8295 kilograms.
