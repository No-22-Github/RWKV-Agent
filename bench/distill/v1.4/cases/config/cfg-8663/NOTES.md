## Traps
- TR-DECOY: HighP95 sits right above with the same thresholds; for: 5m / severity: warning appear twice.
- replace_lines must cover the whole run of 4 lines (start_line 8, end_line 11) and content must have 4 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read monitoring/rules.yaml; the target lines are 8-11.
2. replace_lines start_line 8, end_line 11 with:
         - alert: HighP99
           expr: p99_ms > 1500
           for: 10m
           severity: critical
3. Read monitoring/rules.yaml back to confirm.
Final answer, one sentence then DONE on its own line: Updated monitoring/rules.yaml lines 8-11 (4 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
