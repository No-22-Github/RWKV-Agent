## Traps
- TR-DECOY: Both flags have a percent line; search_v2 must stay at 80. Target line: `  percent: 25       # ramp: 10 -> 25 -> 50` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read flags/rollout.yaml; locate the target line `  percent: 25       # ramp: 10 -> 25 -> 50`.
3. replace_lines that single line with `  percent: 50       # ramp: 10 -> 25 -> 50` (only 25 -> 50).
4. Read flags/rollout.yaml back and confirm only that line changed.
Final answer: 'Updated flags/rollout.yaml: the value is now 50, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
