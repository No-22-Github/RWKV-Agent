## Traps
- TR-AMBIG: every bill carries billed and volumetric weights and the README says chargeable weight is a per-contract choice; reading the volumetric column gives 18145. Turn 1 must name both weight bases and ask which the review uses.

## Reference solution
1. Turn 1: read bills/freight-bills-2026-08.csv, see the two weight columns, name both and ask which basis the review wants.
2. Turn 2: the user picks billed weight.
3. Sum billed_weight_kg over the four bills: 4180+3655+5240+2875.
4. Total 15950 and reply with the number alone.

## Why the answer is unique
 The decoy 18145 sums the volumetric column; with the basis pinned to billed weight the volumetric figures are out of scope, so 15950 is the only reading.

## Five alternative phrasings of the task
1. How much did the August freight weigh in total?
2. Add up the August freight weights.
3. What was the total billed freight weight in August?
4. Give me the August weight total for the review.
5. Sum the freight weights on the August bills.
