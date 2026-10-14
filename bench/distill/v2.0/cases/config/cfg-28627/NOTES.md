## Traps
- TR-DECOY: [app] has an identical line. Target line: `max_size_mb = 100    ; rotate when exceeded` ([audit]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read etc/logrotate.ini; locate the target line `max_size_mb = 100    ; rotate when exceeded`.
3. replace_lines that single line with `max_size_mb = 250    ; rotate when exceeded` (only 100 -> 250).
4. Read etc/logrotate.ini back and confirm only that line changed.
Final answer: 'Updated etc/logrotate.ini: the value is now 250, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
