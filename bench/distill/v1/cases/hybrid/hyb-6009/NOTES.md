## Traps
- TR-AMBIG: the request names Rhiannon while rota/august-2026.csv holds two candidates, Rhiannon Petch and Rhiannon Wynn. Reading it as Rhiannon Wynn gives 34.5; the request was settled on Rhiannon Petch, giving 41.5 (from rota/august-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names Rhiannon but the workspace holds two candidates, Rhiannon Petch and Rhiannon Wynn, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds rota/august-2026.csv and README.md.
3. read rota/august-2026.csv and take the total of the hours column for Rhiannon Petch: 41.5.

## Why the answer is unique
The decoy 34.5 belongs to Rhiannon Wynn; it answers a different candidate, and the request was settled on Rhiannon Petch before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 41.5.

## Five alternative phrasings of the task
1. caldbec vets rhiannon hours august 2026
2. nursing rota for rhiannon petch and rhiannon wynn
3. shift hours per nurse caldbec
4. august payslip query nursing team
5. hours worked by the two rhiannons
