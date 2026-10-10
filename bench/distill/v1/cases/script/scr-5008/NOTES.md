## Traps
- None. No trap tag is set: the sheet layout is in the script's own notes, and the option the club wants is described in the task.

## Reference solution
1. Read usage.py: outings sit in outings/, the columns are date,boat,member,minutes, and the sheet is one line per boat in boat name order plus a totals line (call 1).
2. Read the outing files under outings/ to see the month a date column carries (call 2).
3. Give main() a --month option that keeps only the rows whose date starts with the month it is given, leaving the aggregation, the boat order and the totals line as they are (call 3).

## Why the answer is unique
The option is asked for on the August outings, and August holds exactly two outings: Curlew with 85 minutes and Heron with 110, so the sheet under --month 2026-08 is

    Curlew,85
    Heron,110
    TOTAL,195

The September and October outings sit in the same directory and must not move those figures: the Mallard rows and the later Heron row each carry a month of their own in the date column, so no reading puts them in the August sheet. Leaving the totals line off would break the layout the notes state, and ignoring the month leaves August no different from the unset run.
