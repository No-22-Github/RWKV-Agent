## Traps
- None. No trap tag is set: the fault is a column-name mismatch in the script that reads the export, and the layout the sheet has to keep is stated in that same file.

## Reference solution
1. Read costing.py: its module notes name the export columns job_id,client,sheet_count,ink_ml,rate_pence, while the cost line reads row["ink_units"], a column no export carries (call 1).
2. Replace that one lookup with row["ink_ml"], leaving the layout, the job_id order and the exports under jobs/ as they are (call 2).

## Why the answer is unique
The sheet is fixed by the one mismatch: the export columns are stated in the script, every other line already agrees with them, and the ink charge has no other source in the data. With both monthly exports in place the repaired script prints:

    J-2201,Caldergate Choir,15.60
    J-2202,Harrow Lane Fencing,12.90
    J-2203,Bramblewick Bindery,4.90
    J-2204,Harrow Lane Fencing,10.20
    J-2205,Thornbury Almanacs,19.80
    TOTAL,63.40

A repair that renames the column inside the export instead of inside the code contradicts the record the press keeps for its own jobs, and the October export arrives after the repair, so the export is not the place to put it right.

