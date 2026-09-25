## Traps
- TR-AMBIG: the first message asks how many people came through on the twelfth without naming a gate. The sheet has a North and a South figure for that day (517 and 286), so a first turn that reports either one, or their sum, has guessed; the correct first turn is a question with no tool call. The second turn names the North gate and the answer is 517. The careless answer is the South figure 286.

## Reference solution
1. Turn 1: ask which turnstile the figure is for; no calls.
2. Turn 2 (North gate named): read counts/turnstile-2026-09.csv and take the entries for 2026-09-12 at the North gate. That is 517, a total of 2 calls.

## Why the answer is unique
Once the North gate is named there is exactly one row for it on 12 September, so 517 is the only figure that answers the clarified request. The decoy 286 is the South gate's count for the same day, and the South turnstile is a different gate: the README keeps the two gates apart and the sheet labels every row with its gate, so no reading turns 286 into the North gate's figure. The sum 803 is likewise not a gate figure.
