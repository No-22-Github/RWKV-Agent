## Traps
- TR-SUPERSEDE: the June sheet (published 2026-06-18, effective 15 June 2026) ranks first in search; the September revision (published 2026-09-10, effective 8 September 2026) carries the current rates and supersedes it. Pricing the invoices off the June "We buy GBP" rate gives 12680.00 x 1.1505 = 14588.34 (decoy).
- TR-DIRMAP: on each sheet the first column is "We sell GBP"; the column guide in the page body assigns "We buy GBP" to converting sterling receipts into euros. Using "We sell GBP" on the September sheet gives 12680.00 x 1.1810 = 14975.08 (decoy).

## Reference solution
1. read_file README.md - the revaluation rule: receivables are revalued at the
   quotation in force on the reporting date, not at the invoice-date one (1)
2. datetime - the reporting date, 2026-09-16 on the fixed clock (2)
3. web_search aldermoor bank fx desk rates (3)
4. web_fetch the first sheet; effective 15 June 2026 (4)
5. web_fetch the September revision; effective 8 September 2026, supersedes the June sheet (5)
6. read_file invoices.csv; amount_gbp sums to 12680.00 (6)
7. calculator 12680.00 x 1.1630 ("We buy GBP", September sheet) = 14746.84 (7)
8. answer 14746.84 (8)

ref_calls = 7 (the two web_fetch targets may be fetched in one call).

## Why the answer is unique
README fixes the time basis on the reporting date, so the applicable sheet
is the one in force that day: the September revision is effective 8 September
2026 and the clock reads 2026-09-16, and it explicitly supersedes the June
sheet. The column guide maps sterling receipts to "We buy GBP" unambiguously.
invoices.csv contains only August invoices and every product is exact to the
cent, so no rounding judgement is involved.

## Reviewer notes
- v3 (2026-09-21 audit): the v2 prompt asked for "prevailing desk rates" for a
  set of August invoices and expected the September sheet. That is not a
  unique answer. Converting August receipts at the quotation that was in force
  during August - the June sheet, superseded only on 8 September - is the
  ordinary reading, and 3 of 4 rounds in the 2026-09-21 deepseek-flash run
  answered 14588.34 that way. The decoy was a defensible reading of the
  question, which breaks the bank's own rule that an answer must be unique
  (authoring-guide §1.4). v3 anchors the time basis on the reporting date
  instead, so TR-SUPERSEDE still has to be resolved (which sheet is in force?)
  and TR-DIRMAP still has to be resolved (sell or buy column?), but only one
  reading of the question survives. The expected answer is unchanged; the
  14588.34 decoy is now genuinely wrong rather than merely unintended, and
  reaching the reporting date adds the datetime call to ref_calls.
- v4 (2026-09-21, same round): v3 moved the time basis into the *prompt*, which
  the authoring guide reserves for goals - rules belong in the fixture. It also
  did not work: across three v3 rounds deepseek-flash fetched both sheets and
  the reporting date and still could not commit, thrashing on repeated
  web_search until it burned all 16 steps (k0 and k2) or abstained (k1). The
  model had the evidence and no rule telling it which quotation applies, so it
  kept looking for one. v4 states the revaluation rule in README.md, where a
  rule that governs a calculation belongs, and returns the prompt to a plain
  statement of the goal. TR-SUPERSEDE and TR-DIRMAP are untouched: the model
  still has to work out which sheet is in force and which column applies.

## Five alternative phrasings of the task
1. aldermoor bank fx desk rates
2. aldermoor gbp eur rate
3. aldermoor currency desk september
4. aldermoor bank sterling quotations
5. aldermoor fx rates for business

<!-- WORKBANK-CANARY-5d2b90f3 : this file must never enter training corpora -->
