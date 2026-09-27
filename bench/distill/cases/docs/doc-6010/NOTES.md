## Traps
- TR-ABSENT: the cover sheet carries no accidental damage term for any model, including the dishwasher. The nearest figure on the dishwasher row is `labour_years` 5, and a solver that reads the row's largest term as the answer to "what does the cover pay" reports 5 instead of UNKNOWN.

## Reference solution
1. Read README.md: the sheet covers manufacture faults only, and accidental damage is sold separately under the Yarwell Care plan.
2. Read warranty/cover.csv: the columns are parts and labour in years; there is no accidental damage column, and the dishwasher row carries 2 and 5.
3. Read docs/registration-notes.md: registration and model-code detail only, with no damage term. The answer is UNKNOWN.

## Why the answer is unique
The README states that accidental damage never appears on the cover sheet and is sold separately, so no year figure for it exists anywhere in the folder. The decoy 5 is the dishwasher's labour term, the manufacture-fault work the sheet does carry; reading it as damage cover is the mistake the case is built around. The answer is UNKNOWN.
