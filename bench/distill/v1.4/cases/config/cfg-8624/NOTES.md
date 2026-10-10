## Traps
- TR-DECOY: api has an identical maxReplicas line; only the worker block changes. Target line: `    maxReplicas: 10     # capped by node pool size` (worker:).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read deploy/values.yaml; locate the target line `    maxReplicas: 10     # capped by node pool size`.
3. replace_lines that single line with `    maxReplicas: 14     # capped by node pool size` (only 10 -> 14).
4. Read deploy/values.yaml back and confirm only that line changed.
Final answer: 'Updated deploy/values.yaml: the value is now 14, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
