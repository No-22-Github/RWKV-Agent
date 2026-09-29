## Traps
- TR-ABSENT: the cover sheet carries no accidental damage term for any model, including the dishwasher. The nearest figure on the dishwasher row is `labour_years` 5, and a solver that reads the row's largest term as the answer to "what does the cover pay" reports 5 instead of UNKNOWN.

## Reference solution
1. Read README.md, warranty/cover.csv and docs/registration-notes.md.
2. warranty/cover.csv carries parts and labour years per model, and the dishwasher row carries those two manufacture-fault terms only, with no accidental damage column anywhere on the sheet; README.md states the sheet covers manufacture faults only and that accidental damage is sold separately under the Yarwell Care plan and never appears on the cover sheet, so no years of accidental damage cover exist for the dishwasher in the folder.
3. Final answer in two or three sentences: name the files checked, say the cover sheet carries no accidental damage term for the dishwasher, and point to the dishwasher row's parts and labour terms as different, manufacture-fault cover without quoting their figures. Scored with output_contains_any over "accidental damage", "Accidental damage" or "accidental damage cover"; output_excludes rules out UNKNOWN and the 5-year labour figure, so the reply names the missing cover instead of quoting any year count.

## Why the answer is unique
README.md states that accidental damage never appears on the cover sheet and is sold separately, so no year figure for it exists anywhere in the folder. The decoy 5 is the dishwasher's labour term, the manufacture-fault work the sheet does carry; reading it as damage cover is the mistake the case is built around. The only truthful reply reports the absence: the cover sheet, README.md and the registration notes were checked, no accidental damage term exists on the sheet, and the dishwasher row's labour term is different cover whose figure is not the answer to the question.
