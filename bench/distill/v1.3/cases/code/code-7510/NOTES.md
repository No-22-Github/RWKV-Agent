## Traps
- TR-DECOY: net/policy.py 的注释里留着旧口径 BASE_DELAY_MS = 500，粗读会把起始延时当成 500ms。 A careless pass reports `500`.

## Reference solution
1. Read net/backoff.py for the retry loop and the delay constant.
2. Read net/policy.py and note its comment is the retired tuning.
3. Explain the trigger, the starting delay and the doubling growth.

## Why the answer is unique
The 500 figure lives only in a comment describing the pre-February tuning in policy.py, and backoff.py never references it, so the starting delay is BASE_DELAY_MS = 250. with_backoff retries on ThrottlingError and doubles the delay each round, which pins all three behaviors.
