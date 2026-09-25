## Traps
- TR-AMBIG: the first message asks for the price of a 500 g tin of Dark Roast without saying which list applies. Both lists price it (retail 6.75, trade 5.40), so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn names the retail list and the answer is 6.75. The careless answer is the trade figure 5.40.

## Reference solution
1. Turn 1: ask which list the quote is for; no calls.
2. Turn 2 (retail list named): read price-lists/retail-2026-09.csv and take the price_gbp of DR-500. That is 6.75, a total of 2 calls.

## Why the answer is unique
Only one list can apply once the counter is named: the retail list, and it prices DR-500 at 6.75. The decoy 5.40 is the trade figure for the same tin, and a counter sale cannot be billed at trade rates: the trade list in the same workspace is headed as the cafe-by-the-case list and the README says the retail list is the counter one, so 5.40 is not a reading of the clarified request. Both files carry the same four item codes, so there is no tin that only one list prices.
