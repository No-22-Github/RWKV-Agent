## Traps
- TR-AMBIG: the request names the main meter while readings/august-2026.csv holds two candidates, South Wing and North Wing. Reading it as North Wing gives 2776.9; the request was settled on South Wing, giving 2750.2 (from readings/august-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the main meter but the workspace holds two candidates, South Wing and North Wing, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds readings/august-2026.csv and README.md.
3. read README.md: reads are weekly and each wing reports on its own.
4. read readings/august-2026.csv, keep the South Wing rows for the Main meter, and take the reading on the final read date of August 2026: 2750.2.

## Why the answer is unique
The decoy 2776.9 is North Wing's closing figure; it answers a different wing, and the return was settled on South Wing before a figure was taken.
Readings inside the month are weekly intermediate figures, not the closing one, and rows for other meters or for North Wing are out of scope. The final read date of the month pins one row for South Wing, so the answer is 2750.2.

## Five alternative phrasings of the task
1. selby marine institute main meter closing reading august 2026
2. water meter log for north and south wing
3. campus water return per wing selby
4. august closing figure on the main meter
5. weekly reads at the marine institute
