## Traps
- TR-DECOY: The 3.2.0 entry (untagged) says 9200; 3.0.0 says 9000, the current value.

## Reference solution
1. Read the basis CHANGELOG.md: the new value is 9100.
2. Read src/config.ts: line 2, `ADMIN_PORT = 9000`, is the one to change.
3. replace_lines line 2 with `ADMIN_PORT = 9100`; the rest of the line stays.
4. Read src/config.ts back to confirm.
Final answer example: ADMIN_PORT in src/config.ts is now 9100, matching the 3.1.0 changelog entry; the untagged 3.2.0 change was ignored.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
