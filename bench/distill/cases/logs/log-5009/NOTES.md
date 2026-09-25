## Traps
- TR-ABSENT: the question asks how the accepted SKUs' prices compare with Dunmere's previous list. README.md says the loader writes a line only for the SKUs it turns away, and the run's closing line carries counts alone, so no price of an accepted SKU is recorded anywhere and the comparison cannot be made. The expected answer is UNKNOWN.
- TR-DECOY: two nearby numbers invite a value answer. The closing line reports accepted=44, which is the count of accepted SKUs and says nothing about their prices, and the run's one price_out_of_range rejection looks like a price signal but is a rejected SKU, not an accepted one.

## Reference solution
1. List the workspace: README.md and logs/feed-loader.log.
2. Read README.md. The journal lists rejected SKUs only; accepted SKUs appear as a count on the closing line and their prices are never written down.
3. Read logs/feed-loader.log. Its six rejection lines carry reason codes and no prices, and the closing line reports accepted=44 rejected=6. Nothing compares this list with the previous one.

## Why the answer is unique
The question needs the price of each accepted SKU on this list and on the previous list. The workspace holds neither: the journal names only rejected SKUs, and no file records a price at all. The decoy 44 is the count of accepted SKUs, which is not a price comparison, and 1 is the number of SKUs this run rejected for a price that fell outside the agreed band, which is a rejection rather than a price move. Since the data needed to answer is absent, the only sound reply is UNKNOWN.

## Fixture notes
README.md documents the three reason codes and states that a run lists a rejected SKU once and that the closing line accounts for all of them, so the journal can be read as complete. The sibling cases in this family ask the same shape of question about the same journal format where the journal does hold the answer.
