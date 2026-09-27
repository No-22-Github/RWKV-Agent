## Traps
- None. `receipt_email_prompt` is the only flag whose name names that feature, and its entry carries a single `rollout_pct`, so there is no second value for a solver to weigh against it.

## Reference solution
1. Read README.md: the flag sheet is the only place flags are set, and each entry carries an enabled state and a rollout percentage.
2. Read flags/kiosk-flags.json: the `receipt_email_prompt` entry carries `rollout_pct` 60. The answer is 60.

## Why the answer is unique
The sheet carries one entry per flag and `receipt_email_prompt` is the only entry naming that feature, so 60 is the only percentage attached to it. The 100 on `pin_topup` and the 25 on `quiet_mode_after_22h` belong to other flags, and the enabled state `true` is not a percentage. The answer is 60.
