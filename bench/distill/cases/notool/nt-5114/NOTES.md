## Traps
- TR-AMBIG: the first message asks how many bearing cups can be supplied without saying whether the stock already promised to another order counts, and the card carries both on_hand (148) and available (122), so a first turn that reports either figure has guessed. The correct first turn is a question with no tool call. The second turn rules reserved stock out and the answer is 122. The careless answer is the shelf figure 148.

## Reference solution
1. Turn 1: ask whether reserved stock can be promised; no calls.
2. Turn 2 (only free stock): read stock/parts-2026-09.csv and take the available figure for BC-220. That is 122, a total of 2 calls.

## Why the answer is unique
The card gives every row an available column, and BC-220 is the only bearing cup row, so 122 answers the clarified request. The decoy 148 is the on_hand figure for the same part, and the README defines reserved as stock promised to another order and available as the difference, so a request for what can be promised cannot include the 26 cups already committed. The other rows are different parts.
