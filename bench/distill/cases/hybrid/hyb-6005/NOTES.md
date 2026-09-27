## Traps
- TR-AMBIG: the request names the Long Meadow while spraying/july-2026.csv holds two candidates, Grange Farm and Mill Farm. Reading it as Mill Farm gives 16; the request was settled on Grange Farm, giving 29.25 (from spraying/july-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Long Meadow but the workspace holds two candidates, Grange Farm and Mill Farm, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds spraying/july-2026.csv and README.md.
3. read spraying/july-2026.csv and take the total of the hectares column for Grange Farm: 29.25.

## Why the answer is unique
The decoy 16 belongs to Mill Farm; it answers a different candidate, and the request was settled on Grange Farm before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 29.25.

## Five alternative phrasings of the task
1. tarnvale agri services long meadow spraying july 2026
2. spray passes at mill farm and grange farm
3. july hectares per field tarnvale
4. long meadow spray job sheets
5. hectares sprayed before the farm invoices
