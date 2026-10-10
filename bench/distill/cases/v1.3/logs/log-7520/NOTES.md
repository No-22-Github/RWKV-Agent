## Traps
- TR-SUPERSEDE: notes/payout-runbook.md is v2 (effective 2026-09-01) and its changelog says the v1 sheet checked the limit against the NET amount. Reasoning from the net figure (~46k < 50k, as the user does in turn 4) makes the limit check look impossible and mis-points the failure; v2 checks GROSS, and the log's own ERROR line prints batch gross 51,340.22 GBP against the 50,000.00 GBP limit.

## Reference solution
1. Turn 1: read logs/payout-batch.csv: fx-convert completes at 02:11:58; the ERROR at 02:14:07 is on [step:fund-release]. Answer: fund-release.
2. Turn 2: that ERROR line is timestamped 02:14:07. Answer: 02:14 (02:14:07).
3. Turn 3: the follow-up line at 02:14:08 reads released 118 items. Answer: 118 items.
4. Turn 4: read notes/payout-runbook.md: v2 (in force) checks the GROSS amount; the log's gross is 51,340.22 GBP, so the batch exceeded the limit by 51,340.22 - 50,000.00 = 1,340.22. Answer: 1340.22 (1,340.22).
5. Turn 5: the same line reports 42 items pending. Answer: 42 items.

## Why the answer is unique
The log names exactly one failed step and one ERROR timestamp, and the release line states the released/pending split (118 + 42 = 160, matching the batch start line). The runbook's changelog pins which limit rule is in force, and the gross figure is printed in the ERROR line itself, so the overrun is a single subtraction; the net-based reading the user brings is the superseded v1 rule the changelog retires.
