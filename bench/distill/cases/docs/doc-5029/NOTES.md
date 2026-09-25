## Traps
- TR-MULTISRC: the named documents are split between `lists/stage-set.txt` and `lists/office-set.txt`. The stage list alone is short of 2 documents (`forms/get-in-schedule.md` and `forms/risk-assessment.md`) and the office list alone is short of 2 (`budgets/production-budget.csv` and `forms/risk-assessment.md`), so working from either list by itself gives the decoy 2.
- TR-DUPROW: `forms/risk-assessment.md` is named by both lists, so counting lines rather than documents gives 4 while the folders are short of 3 distinct documents.

## Reference solution
1. List the workspace: a cover note, the two lists and three documents held in the folders.
2. Read `lists/stage-set.txt`: forms/get-in-schedule.md, scripts/lighting-plot.md, forms/risk-assessment.md, notes/wardrobe-hire.md.
3. Read `lists/office-set.txt` and fold it in: budgets/production-budget.csv, scripts/lighting-plot.md, forms/risk-assessment.md, licences/music-licence.md. Against the documents present in the folders, the missing ones are forms/get-in-schedule.md, forms/risk-assessment.md and budgets/production-budget.csv, which is 3.

## Why the answer is unique
The decoy 2 is wrong because neither list is the whole set of named documents: each list is short of two documents on its own, and the union of the two names three distinct ones. The decoy 4 is wrong because forms/risk-assessment.md is named by both lists yet is still one missing document, and the question asks how many documents are absent rather than how many lines name one. scripts/lighting-plot.md, notes/wardrobe-hire.md and licences/music-licence.md are named and present, so they do not count. The answer is 3.
