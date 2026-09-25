## Traps
- TR-AMBIG: the first message asks what erecting the twelve by eighteen marquee costs without saying which day the wedding falls on. The tariff sheet carries both columns (weekday 715.00, Saturday 890.00) and nothing in the workspace gives the wedding date, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn says Saturday and the answer is 890.00. The careless answer is the weekday figure 715.00.

## Reference solution
1. Turn 1: ask which day of the week the wedding falls on; no calls.
2. Turn 2 (Saturday named): read tariffs/erection-2026-09.csv and take the saturday_gbp of the 12 m x 18 m row. That is 890.00, a total of 2 calls.

## Why the answer is unique
Once the day is named there is one column left: the Saturday one, and the 12 m x 18 m row gives 890.00. The decoy 715.00 is the weekday figure for the same size, and the README says Saturday work is quoted from the Saturday column, so 715.00 cannot answer a Saturday job. Nothing in the workspace says when the Hartley wedding is, so the choice is the requester's and no reading of the workspace settles it before the second turn.
