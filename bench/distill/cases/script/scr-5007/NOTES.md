## Traps
- None. No trap tag is set: the layout the sheet has to keep is stated in the script's own notes, and the fault is in the amount formatting.

## Reference solution
1. Read churns.py: its module notes say amounts print in pounds with two decimals, while pounds() joins the pence remainder onto the pounds with "%d.%d", so a remainder under ten loses its leading zero (call 1).
2. Change that one format to "%d.%02d", leaving the collection walk, the ordering and the files under collections/ as they are (call 2).

## Why the answer is unique
Every collection is churns times rate_pence, and the sheet is the per-collection line plus a totals line. With both monthly files in place the repaired script prints:

    2026-08-04,Netherby Farm,180.00
    2026-08-07,Bracken Hollow,112.50
    2026-08-13,Netherby Farm,225.00
    2026-08-18,Rushmere Croft,122.50
    2026-08-22,Bracken Hollow,137.50
    2026-09-02,Rushmere Croft,175.00
    2026-09-09,Netherby Farm,210.00
    2026-09-15,Bracken Hollow,100.00
    TOTAL,1262.50

No other reading moves a figure: every amount is a whole number of pence, each row carries its own rate, and the only difference between the sheet as it should read and the sheet as it reads now is the number of decimals, so the fault can only live in the format. Editing a rate in collections/ to force the printed figure would move the pence digits rather than the decimals and contradicts the round record that file is.
