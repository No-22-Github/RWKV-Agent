## Traps
- TR-RULEFILE: milling_terms.md holds the toll rates and they differ by grain, so no figure in the request or in
  the intake log gives the toll. Treating every load at the bread wheat rate gives 79756.8.
- TR-DECOY: archive/milling_terms_2023.md is the same kind of card with higher rates, so a reader who takes that
  card instead of the current terms answers 72970.2.

## Reference solution
1. List the workspace: the August intake log, the mill's milling terms, an archive directory and a short readme.
2. Read milling_terms.md: the toll is 96 kilograms per tonne of bread wheat, 61 for feed wheat and 78 for rye.
   The card in archive/ is an earlier season's and does not apply to the August 2026 intake.
3. Read intake_2026-08.csv and add the tonnes by grain.
4. Multiply each grain's tonnage by its rate and add: 63390.6 kilograms.

## Why the answer is unique
The toll is a share of the grain and its size depends on the grain, so it can only be worked out from the terms
that set the rates; the request states no rate and the log carries no toll column. Every load names one of the
three grains the card rates, so each row has exactly one rate. Reading a different card, or applying one rate to
all three grains, changes the figure, so 63390.6 kilograms is the only answer the workspace supports.
