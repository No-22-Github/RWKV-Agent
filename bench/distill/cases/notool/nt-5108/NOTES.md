## Traps
- TR-AMBIG: the first message asks for the shortfall figure without saying where to take it. The workspace holds two versions, notes/claim-draft.txt at 19004.10 and the finance export line F-01 at 18420.55, so a first turn that gives either figure has guessed. The correct first turn is a question with no tool call. The second turn rules the draft out and the answer is 18420.55. The careless answer is 19004.10.

## Reference solution
1. Turn 1: ask which record the figure should come from; no calls.
2. Turn 2 (finance export named): read figures/august-2026.csv and take amount_gbp for line F-01, the Bramfield contract shortfall. That is 18420.55, a total of 2 calls.

## Why the answer is unique
Line F-01 is the only export line described as the Bramfield contract shortfall, so 18420.55 is the figure for the clarified request; F-03 is Bramfield haulage, a different line. The decoy 19004.10 comes from the unchecked draft, and the README says the draft was typed while the figures were moving and never checked against the export, so once the export is named the draft cannot supply the claim figure.
