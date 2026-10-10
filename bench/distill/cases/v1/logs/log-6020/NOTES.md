## Traps
- TR-CLAIM: the closing SUMMARY line reports exceptions=0 and calls the reconciliation clean, while the check lines show BK-6118 with card_check cvv_mismatch. Taking the banner at its word leads to replying UNKNOWN.

## Reference solution
1. List the workspace: README.md and logs/reconciliation.log.
2. Read README.md: each check line records its own result; the SUMMARY is composed from counters at the end of the run.
3. Read logs/reconciliation.log and take the booking reference from the single card_check cvv_mismatch line = BK-6118.

## Why the answer is unique
Each check line carries the result for exactly one booking, and exactly one line records a mismatch, so the evidence names one reference with no second candidate. The SUMMARY's exceptions=0 conflicts with the itemised lines it is supposed to summarise, and the README's provenance note gives no basis for preferring the counter over the evidence; reading the banner and giving up is the decoy, not a second reading of the checks. The evidence yields BK-6118.
