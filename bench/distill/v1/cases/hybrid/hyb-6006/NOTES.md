## Traps
- TR-AMBIG: the request names the Top Paddock while baling/april-2026.csv holds two candidates, Fernhill Farm and Fernshaw Farm. Reading it as Fernshaw Farm gives 60; the request was settled on Fernhill Farm, giving 118 (from baling/april-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Top Paddock but the workspace holds two candidates, Fernhill Farm and Fernshaw Farm, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds baling/april-2026.csv and README.md.
3. read baling/april-2026.csv and take the total of the bales column for Fernhill Farm: 118.

## Why the answer is unique
The decoy 60 belongs to Fernshaw Farm; it answers a different candidate, and the request was settled on Fernhill Farm before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 118.

## Five alternative phrasings of the task
1. stennack agri top paddock bales april 2026
2. baling runs at fernhill and fernshaw
3. april bale counts per field stennack
4. top paddock loads off the baler
5. bales carted for the annual statements
