## Traps
- TR-AMBIG: the request names Tomas while bakes/july-2026.csv holds two candidates, Tomas Brierley and Tomas Kubiak. Reading it as Tomas Kubiak gives 8; the request was settled on Tomas Brierley, giving 9 (from bakes/july-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names Tomas but the workspace holds two candidates, Tomas Brierley and Tomas Kubiak, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds bakes/july-2026.csv and README.md.
3. read bakes/july-2026.csv and take the count of rows for Tomas Brierley: 9.

## Why the answer is unique
The decoy 8 belongs to Tomas Kubiak; it answers a different candidate, and the request was settled on Tomas Brierley before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 9.

## Five alternative phrasings of the task
1. ledbury bakehouse tomas batches july 2026
2. bake log for tomas brierley and tomas kubiak
3. batches mixed per baker ledbury
4. july tally for the summer bonus
5. baker totals in the bakehouse log
