## Traps
- TR-DECOY: The test stage has the same key; only the build stage changes. Target line: `    timeout_minutes: 20   # was 15 before the monorepo split` (  build:).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read .ci/pipeline.yml; locate the target line `    timeout_minutes: 20   # was 15 before the monorepo split`.
3. replace_lines that single line with `    timeout_minutes: 25   # was 15 before the monorepo split` (only 20 -> 25).
4. Read .ci/pipeline.yml back and confirm only that line changed.
Final answer: 'Updated .ci/pipeline.yml: the value is now 25, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
