## Traps
- None. No trap tag is set: the sheet layout is stated in the script itself, the shade column is
  written by hand on the range, and a later monthly file only has to be picked up the same way.

## Reference solution
1. Read dyelots.py: its module notes name the lots/ directory with one file per month, the columns
   and the printed layout, while the option handling is missing (call 1).
2. Add a --shade option that keeps the lot rows whose shade matches the name given and adds up
   only those rows for the totals line, leaving everything else as it is (call 2).

## Why the answer is unique
The sheet for the re-dye order prints the indigo lots in lot_no order, with the totals line
summing only those lots:

    WX-2401,indigo,180
    WX-2403,indigo,220
    WX-2406,indigo,130
    WX-2409,indigo,155
    TOTAL,685

Printing the whole sheet under the option contradicts the request, and adding up the unfiltered
lots gives 1130, which is not a total of the lots the sheet prints. The answer is 685.
