## Traps
- TR-ABSENT: the flag sheet carries no `gift_receipt_printing` entry. The nearest entry is `receipt_email_prompt` with `rollout_pct` 60, and a solver that reads the two receipt features as one reports 60 instead of UNKNOWN.

## Reference solution
1. Read README.md: a flag that is not on the sheet is not part of the kiosk build, and the sheet is the only place flags are set.
2. Read flags/kiosk-flags.json: the entries are `receipt_email_prompt`, `pin_topup`, `seat_upgrade_offer` and `quiet_mode_after_22h`; gift receipt printing is not among them.
3. Read docs/kiosk-runbook.md: printed gift receipts are handled by the receipt printer's own menu, outside the flag sheet. The answer is UNKNOWN.

## Why the answer is unique
The README states that the sheet is the only place flags are set and that a flag off the sheet is not part of the build, so a feature the sheet does not list has no rollout figure at all. The decoy 60 is the rollout of `receipt_email_prompt`, an email prompt at the end of the sale, not printed gift receipts; reading one receipt feature as the other is the mistake the case is built around. The answer is UNKNOWN.
