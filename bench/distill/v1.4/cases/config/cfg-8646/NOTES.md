## Traps
- TR-DECOY: web has the same cpu_percent line; do not touch it. Target line: `    cpu_percent: 80     # page after 10m` (  batch:).

## Reference solution
1. Read monitoring/ticket-77.txt: new value 90
2. Read monitoring/alerts.yaml; locate the target line `    cpu_percent: 80     # page after 10m`.
3. replace_lines that single line with `    cpu_percent: 90     # page after 10m` (only 80 -> 90).
4. Read monitoring/alerts.yaml back and confirm only that line changed.
Final answer: 'Updated monitoring/alerts.yaml: the value is now 90, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
