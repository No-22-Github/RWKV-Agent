## Traps
- TR-DECOY: Entries are out of order; 100 and 50 appear as older values and 50 is the file's current value.

## Reference solution
1. Read the basis CHANGELOG.md: the new value is 75.
2. Read lib/paging.rb: line 2, `PAGE_SIZE = 50`, is the one to change.
3. replace_lines line 2 with `PAGE_SIZE = 75`; the rest of the line stays.
4. Read lib/paging.rb back to confirm.
Final answer example: PAGE_SIZE in lib/paging.rb is now 75, from the 2026-09-20 changelog entry.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
