## Traps
- None. No trap tag is set: the export shape and the printed layout are stated in the notes the
  script carries, and the later monthly export only has to be picked up the same way.

## Reference solution
1. Read daybook.py: its notes name the tills/ directory with one export per month, the keys the
   sales carry and the printed layout; read the September export to see the shape (call 1).
2. Write the daybook so every export in tills/ is read, the sales are grouped by day, the days
   print in date order and the totals line adds up all of them (call 2).

## Why the answer is unique
The daybook prints one line per day with that day's sale count and takings, then the totals line:

    2026-09-04,2,2030
    2026-09-12,1,540
    2026-09-19,2,1340
    2026-10-02,1,620
    2026-10-11,1,1180
    TOTAL,7,5710

Reading only the September export and stopping there prints five fewer sales and 5710 less in the
totals, and the request names the later exports as well. The answer is 5710.
