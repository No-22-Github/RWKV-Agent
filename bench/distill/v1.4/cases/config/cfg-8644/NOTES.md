## Traps
- TR-DECOY: retries_delay_ms starts with the same word; leave it. Target line: `  retries: 5            # exponential backoff` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read client/upload.yaml; locate the target line `  retries: 5            # exponential backoff`.
3. replace_lines that single line with `  retries: 3            # exponential backoff` (only 5 -> 3).
4. Read client/upload.yaml back and confirm only that line changed.
Final answer: 'Updated client/upload.yaml: the value is now 3, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
