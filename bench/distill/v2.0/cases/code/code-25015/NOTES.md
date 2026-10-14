## Traps
- None. No trap tag is set: the wait the question asks about is the constant the scheduler loops over, and the module it lives in is imported by name.

## Reference solution
1. Read press/scheduler.py: press() loops over STUCK_POLLS and raises once the loop runs out (call 1).
2. Read press/limits.py: STUCK_POLLS is 7, so the scheduler polls seven times before it gives up (call 2). The answer is 7.

## Why the answer is unique
The loop is for _ in range(STUCK_POLLS), so the body runs once per poll and the scheduler gives up after the last one: the number of polls is the constant itself, and there is no other bound on the loop in the module. STUCK_POLL_SECONDS sets how long each wait lasts, not how many there are, so no other reading of the two files yields a different poll count. The answer is 7.
