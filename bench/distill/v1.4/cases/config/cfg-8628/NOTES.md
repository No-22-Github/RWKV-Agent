## Traps
- TR-DECOY: ttl_seconds_error shares the key prefix; do not touch it. Target line: `    ttl_seconds: 3600       # images, css, js` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read cdn/cache.yaml; locate the target line `    ttl_seconds: 3600       # images, css, js`.
3. replace_lines that single line with `    ttl_seconds: 7200       # images, css, js` (only 3600 -> 7200).
4. Read cdn/cache.yaml back and confirm only that line changed.
Final answer: 'Updated cdn/cache.yaml: the value is now 7200, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
