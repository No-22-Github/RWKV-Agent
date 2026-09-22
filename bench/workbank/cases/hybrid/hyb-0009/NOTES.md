## Traps
- None (L0 baseline). The prompt names no file and the workspace carries one data table, so the only work is to find the published rate and apply it to the register's total tonnage. Untagged by design: there is no competing reading of the rate and no second source to trip over.

## Reference solution
1. web_search for the Cormorant Point Navigation Authority light dues page (1)
2. web_fetch the page; the published rate is EUR 1.28 per gross tonne (2)
3. read_file fleet/gross-tonnage.csv; the five vessels sum to 8200 gross tonnes, and 8200 x 1.28 = 10496.00 (3); answer 10496.00

## Why the answer is unique
The authority publishes exactly one light-dues rate (EUR 1.28 per gross tonne) and the workspace holds exactly one tonnage register, whose five rows are the whole fleet. README.md states that dues are assessed on the total gross tonnage, so the base is the plain sum 8200 and the product is exact to the cent. There is no second rate sheet and no per-vessel variation, so no other reading of the question produces a number.

## Five alternative phrasings of the task
1. cormorant point navigation authority light dues rate
2. cormorant point navigation light dues per tonne
3. cormorant point navigation annual light dues
4. cormorant point navigation authority charges
5. cormorant point navigation dues tariff 2026

<!-- WORKBANK-CANARY-3b7f10ac : this file must never enter training corpora -->
