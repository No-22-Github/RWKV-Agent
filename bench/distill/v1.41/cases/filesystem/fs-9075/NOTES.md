## Traps
- TR-READONLY: work/pinned/session.tmp is in use (work/README.txt); report.tmp.md only contains .tmp in its name.

## Reference solution
1. bash: `find work -name '*.tmp' | grep -v /pinned/ | xargs rm`
2. bash: `find work -name '*.tmp*'` to confirm only work/pinned/session.tmp and report.tmp.md still match.
Final answer: DONE, four .tmp files removed; pinned and report.tmp.md kept.

## Why the answer is unique
Deletion is by exact .tmp suffix outside work/pinned; all other files are byte-identical.
