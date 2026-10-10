## Traps
- None. No trap tag is set: the layout and the meaning of the weight column are stated in the
  script itself, and the fault is a single wrong quantity.

## Reference solution
1. Read castings.py: its module notes say the sheet's weight column is the weight of the whole
   casting, while the run prints the weight of one bell (call 1).
2. Multiply the bells by the single-bell weight for the printed line, leaving the layout and the
   castings/ sheets as they are (call 2).

## Why the answer is unique
The despatch sheet prints one line per casting with the casting's weight and then the totals line:

    BM-3120,bronze,105.00
    BM-3121,brass,37.80
    BM-3122,bronze,165.60
    BM-3123,gilt,50.40
    BM-3124,brass,48.60
    BM-3125,bronze,131.25
    TOTAL,538.65

A repair that keeps the per-bell figure prints 8.75 for the first casting, which is what the office
already rejected. The answer is 538.65.
