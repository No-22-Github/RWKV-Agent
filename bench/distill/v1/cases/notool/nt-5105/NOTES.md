## Traps
- TR-AMBIG: the first message asks for the cost of the Aberdeen pallet without naming a carrier. The lane sheet prices both carriers (Northline 48.50, Glenmore Freight 41.20), so a first turn that quotes either has guessed; the correct first turn is a question with no tool call. The second turn names Northline and the answer is 48.50. The careless answer is 41.20.

## Reference solution
1. Turn 1: ask which carrier the pallet is booked with; no calls.
2. Turn 2 (Northline named): read haulage/lane-rates-2026-09.csv and take the Aberdeen row for Northline. That is 48.50, a total of 2 calls.

## Why the answer is unique
Every lane row carries its carrier, so naming Northline leaves exactly one Aberdeen rate, 48.50. The decoy 41.20 is Glenmore Freight's rate on the same lane: a different carrier with a slower transit, and the README says the two are booked under different circumstances, so 41.20 cannot be read as Northline's charge. The Inverness rates belong to another lane.
