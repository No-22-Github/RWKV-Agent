## Traps
- None. No trap tag is set: the sheets and the layout the script has to keep are stated in the script itself, and the fault is a single hard-coded sheet name.

## Reference solution
1. Read crossings.py: its module notes name the crossings/ directory with one sheet per month, the columns and the printed layout, while the load path is pinned to crossings/september.csv, a name no sheet carries (call 1).
2. Rewrite that load path so the sheet is built from the .csv files sitting in crossings/, leaving the layout, the fare arithmetic and the sheets under crossings/ as they are (call 2).

## Why the answer is unique
The crossings are the rows of the monthly sheets, and a crossing prints as <sailed_on>,<route>,<fare> in sailed_on order with a trailing totals line. With both sheets in place the repaired script prints:

    2026-09-03,Harbour Reach,38.70
    2026-09-06,Saltings Point,45.00
    2026-09-11,Harbour Reach,25.80
    2026-09-19,Saltings Point,55.80
    2026-09-24,North Quay,23.40
    2026-10-02,North Quay,36.40
    2026-10-05,Harbour Reach,45.15
    2026-10-09,Saltings Point,28.80
    TOTAL,299.05

A repair that renames the sheet on disk instead of in the code contradicts the ticket office record the crossings/ sheets are, and the October sheet arrives after the repair, so the sheets are not the place to put it right.
