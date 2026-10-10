## Traps
- TR-DECOY: The ticket's other item is blocked and must not be applied. Target line: `burst = 10     # allow short spikes` ([login]).

## Reference solution
1. Read tickets/GW-318.txt: new value 20
2. Read gateway/limits.toml; locate the target line `burst = 10     # allow short spikes`.
3. replace_lines that single line with `burst = 20     # allow short spikes` (only 10 -> 20).
4. Read gateway/limits.toml back and confirm only that line changed.
Final answer: 'Updated gateway/limits.toml: the value is now 20, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
