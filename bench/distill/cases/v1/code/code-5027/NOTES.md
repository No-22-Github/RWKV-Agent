## Traps
- None. No trap tag is set: the module notes and the return branch state what the quote does with
  a run that holds no crates.

## Reference solution
1. Read orders/quote.py: the charge for a run of crates is the per-crate rate, with a floor
   returned when the run holds no crates (call 1).
2. Read the floor constant, MIN_CHARGE_PENCE, which is 420 (call 2).

## Why the answer is unique
The empty order falls into the branch that returns MIN_CHARGE_PENCE, so the quote comes back with
420 pence; multiplying the per-crate rate by nothing would give 0, and that branch is reached
only for a run that holds at least one crate. The answer is 420.
