## Traps
- TR-SUPERSEDE: the June sheet (published 2026-06-18, effective 15 June 2026) ranks first in search; the September revision (published 2026-09-10, effective 8 September 2026) carries the current rates and supersedes it. Pricing the invoices off the June "We buy GBP" rate gives 12680.00 x 1.1505 = 14588.34 (decoy).
- TR-DIRMAP: on each sheet the first column is "We sell GBP"; the column guide in the page body assigns "We buy GBP" to converting sterling receipts into euros. Using "We sell GBP" on the September sheet gives 12680.00 x 1.1810 = 14975.08 (decoy).

## Reference solution
1. web_search aldermoor bank fx desk rates (1)
2. web_fetch the first sheet; effective 15 June 2026 (2)
3. web_fetch the September revision; effective 8 September 2026, supersedes the June sheet (3)
4. read_file invoices.csv; amount_gbp sums to 12680.00 (4)
5. calculator 12680.00 x 1.1630 ("We buy GBP", September sheet) = 14746.84 (5)
6. answer 14746.84 (6)

## Why the answer is unique
The September sheet explicitly supersedes the June sheet and carries the later effective date (fixed clock 2026-09-16), and the column guide maps sterling receipts to "We buy GBP" unambiguously; invoices.csv contains only August invoices. Every product involved is exact to the cent, so no rounding judgement is involved.

## Five alternative phrasings of the task
1. aldermoor bank fx desk rates
2. aldermoor gbp eur rate
3. aldermoor currency desk september
4. aldermoor bank sterling quotations
5. aldermoor fx rates for business

<!-- WORKBANK-CANARY-5d2b90f3 : this file must never enter training corpora -->
