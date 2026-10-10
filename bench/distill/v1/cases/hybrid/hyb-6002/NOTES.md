## Traps
- TR-AMBIG: the request names the Tern while crossings/august-2026.csv holds two candidates, Tern of Sula and Tern of Mara. Reading it as Tern of Mara gives 41; the request was settled on Tern of Sula, giving 57 (from crossings/august-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Tern but the workspace holds two candidates, Tern of Sula and Tern of Mara, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds crossings/august-2026.csv and README.md.
3. read crossings/august-2026.csv and take the total of the vehicles column for Tern of Sula: 57.

## Why the answer is unique
The decoy 41 belongs to Tern of Mara; it answers a different candidate, and the request was settled on Tern of Sula before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 57.

## Five alternative phrasings of the task
1. wraycastle ferries tern vehicles august 2026
2. crossings by the tern of sula in august
3. landing dues tally per hull wraycastle
4. tern of mara and tern of sula crossings
5. august vehicle counts for the tern ferry
