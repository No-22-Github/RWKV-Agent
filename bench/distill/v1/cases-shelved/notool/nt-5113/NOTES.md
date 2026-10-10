## Traps
- TR-AMBIG: the first message asks what a club would pay each month without giving its size, and the group rate has two size bands (44.00 up to 10 people, 62.50 from 11), so a first turn that quotes either band has guessed. The correct first turn is a question with no tool call. The second turn gives thirteen people and the answer is 62.50. The careless answer is the small-group figure 44.00.

## Reference solution
1. Turn 1: ask how many people are on the membership; no calls.
2. Turn 2 (thirteen people): read memberships/2026-09-plans.csv and take the group row whose term covers the size. That is 62.50, a total of 2 calls.

## Why the answer is unique
Thirteen people is past the 10-person split, so only the larger group term answers the clarified request, at 62.50. The decoy 44.00 is the group rate that stops at ten people, and the README says the size is asked for before quoting, so 44.00 cannot cover a thirteen-person membership. The single and household rates are other plans.
