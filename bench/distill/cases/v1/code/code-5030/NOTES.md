## Traps
- TR-DECOY: the store also carries grade_oysters, a helper that tags a whole day as one lot, so a
  count that takes every mention of the name reaches 4.

## Reference solution
1. Read the beds and trays modules and find the import each carries for grade_oyster (call 1).
2. Count the calls: beds/claim.py has one, beds/relay.py has one, trays/counts.py has one
   (call 2).
3. trays/store.py defines both helpers; trays/counts.py calls grade_oysters as well, and that
   call belongs to the other helper (call 3).

## Why the answer is unique
The three call sites of grade_oyster are the claim, the relay and the tally. grade_oysters is a
separate helper with its own call, so counting every match of the name gives 4. The answer is 3.
