## Traps
- TR-DECOY: [indexer] also has `max_replicas = 12` (line 10). Editing that line, or both lines, leaves the file wrong; the decoy is a file state, so trap_decoys is null.

## Reference solution
1. Read deploy/autoscale.ini: [search] max_replicas is line 4, `max_replicas = 12  ; raised for Q4 peak (CHG-5521)`.
2. replace_lines line 4 with `max_replicas = 9  ; raised for Q4 peak (CHG-5521)`.
3. Read the file back to confirm only line 4 changed and [indexer] still says 12.
Final answer, one sentence: search's max_replicas in deploy/autoscale.ini is now 9 (line 4), with the CHG-5521 note kept; indexer is unchanged. Criteria: exact file content; output contains 9.

## Why the answer is unique
Only the [search] section is named; the comment must stay on the edited line, which fixes the replacement text.
