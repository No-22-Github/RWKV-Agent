## Traps
- sqlite3 is not installed (`command not found`, exit 127); the dump has to be counted as text.
- TR-DECOY: overdue_waived rows and the `-- status values` comment contain the word overdue; `grep -c overdue` gives 180. data/README.md says waived loans are no longer overdue.

## Reference solution
1. bash: `sqlite3 :memory: < data/library.sql ...` -> exit 127.
2. bash: `grep -c "'overdue');" data/library.sql`
Final answer: 127 loans have status 'overdue' (counted straight from the INSERT lines because sqlite3 is not available; overdue_waived rows are excluded).

## Why the answer is unique
Every INSERT ends with the status literal followed by `);`.
