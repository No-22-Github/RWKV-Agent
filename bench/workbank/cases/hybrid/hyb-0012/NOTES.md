## Traps
- TR-DIRMAP: the desk sheet lists "We sell AUD" (0.6170) first and "We buy AUD" (0.6035) second; the page's column guide assigns "We buy AUD" to converting Australian dollar receipts into euros. Reading the first, larger column gives 20000.00 x 0.6170 = 12340.00, less the 85.00 charge, i.e. 12255.00 (decoy).
- TR-RULEFILE: the handling charge lives only in finance/policy.md, is not restated on the page or in README.md, and applies at AUD 20,000.00 or more. The batch sums to exactly 20000.00, so it sits on the boundary and the charge is due. Converting correctly but never reading the local file gives 20000.00 x 0.6035 = 12070.00 (decoy).

## Reference solution
1. web_search for Meridian Commerce Bank's desk rates (1)
2. web_fetch the desk sheet; the column guide maps receipts converted into euros to "We buy AUD" = 0.6035 (2)
3. read_file finance/policy.md; a handling charge of EUR 85.00 applies at a converted principal of AUD 20,000.00 or more (3)
4. read_file invoices.csv; amount_aud sums to exactly 20000.00, so the charge is due (4)
5. calculator 20000.00 x 0.6035 = 12070.00, less 85.00 = 11985.00 (5); answer 11985.00

## Why the answer is unique
The desk quotes one pair and its column guide assigns exactly one of the two quotations to converting AUD receipts into euros, so the rate is fixed; the prompt asks for the amount the desk credits, and finance/policy.md is the only place the deduction is defined. The registered decoys are each wrong for a concrete reason. 12070.00 is wrong because it ignores the handling charge: the policy file makes the charge due at a converted principal of AUD 20,000.00 or more and the ledger sums to exactly 20000.00, so treating the threshold as strictly "more than" (a reading the file's "or more" rules out) understates the deduction by 85.00. 12255.00 is wrong because it prices the batch at the desk's quotation for when you purchase Australian dollars from it, whereas Fairhaven is selling Australian dollar receipts to the desk, and it is additionally the value you reach only by ignoring the charge. The invoices carry two decimals and the rate four, so the product is exact to the cent and no rounding judgement is involved.

## Five alternative phrasings of the task
1. meridian commerce bank fx desk rates
2. meridian commerce bank aud eur quotation
3. meridian commerce bank desk rates today
4. meridian commerce bank foreign exchange for business
5. meridian commerce bank currency quotations

<!-- WORKBANK-CANARY-e14b7d90 : this file must never enter training corpora -->
