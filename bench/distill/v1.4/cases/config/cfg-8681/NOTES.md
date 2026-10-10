## Traps
- TR-DECOY: The notes also list an rc2 preview (staging only) and the previous production tag, which is the file's current value.

## Reference solution
1. Read the basis release/NOTES-2026-09.md: the new value is 3.8.4.
2. Read deploy/compose.yaml: line 3, `registry.local/gateway:3.8.1`, is the one to change.
3. replace_lines line 3 with `registry.local/gateway:3.8.4`; the rest of the line stays.
4. Read deploy/compose.yaml back to confirm.
Final answer example: deploy/compose.yaml now uses gateway:3.8.4, the version the notes say went to production on 2026-09-14. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
