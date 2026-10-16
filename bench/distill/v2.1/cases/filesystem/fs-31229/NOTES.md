## Traps
- TR-ABSENT: db-2026-09-15.sql 不在工作区。
- TR-NEARNAME: The manifest confirms the dump was never written.

## Reference solution
No 09-15 dump exists; MANIFEST explains the job failed.

## Why the answer is unique
List backup/ and read MANIFEST: 09-15 missing, job failed.
