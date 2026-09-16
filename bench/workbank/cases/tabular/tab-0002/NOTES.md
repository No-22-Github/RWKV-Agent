## Traps
- TR-SIGN: credit-notes.csv stores every credit as a positive figure; the
  README (billing export notes) states that a credit reduces the balance
  due on the referenced invoice. A model that treats the positive credits
  as money flowing toward us and adds them gets 18672.90 (registered
  decoy). A model that ignores the credit file entirely gets 17881.45,
  which is also wrong. Neither equals the correct 17090.00.

## Reference solution
1. read_file README.md - credit amounts are positive and reduce the
   balance due on the referenced invoice (1)
2. read_file invoices.csv - six invoices issued 2026-01-05..2026-03-30,
   billed total 17881.45 (2)
3. read_file credit-notes.csv - four credits, total 791.45 (3)
4. calculator - 17881.45 - 791.45 = 17090.00 (4)

## Why the answer is unique
All six invoices were issued inside Q1 2026, and every credit references
one of those six invoices, so the whole export is in scope. The README
pins the direction of the credit amounts (positive figure, reduces the
balance), and no other adjustment source exists in the workspace.

<!-- WORKBANK-CANARY-b4e90f15 : this file must never enter training corpora -->
