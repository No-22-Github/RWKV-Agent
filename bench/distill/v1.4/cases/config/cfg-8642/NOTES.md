## Traps
- TR-DECOY: [orders] has an identical retention line. Target line: `retention_hours = 72    ; replay window` ([clicks]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read kafka/topics.ini; locate the target line `retention_hours = 72    ; replay window`.
3. replace_lines that single line with `retention_hours = 168    ; replay window` (only 72 -> 168).
4. Read kafka/topics.ini back and confirm only that line changed.
Final answer: 'Updated kafka/topics.ini: the value is now 168, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
