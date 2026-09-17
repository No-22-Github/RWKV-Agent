## Traps
- TR-SUPERSEDE: policy/claims-timing-memo.md (issued 12 November 2025) sets a 60-day window; policy/expense-window-memo.md (issued 9 March 2026) sets 45 days and explicitly replaces the November memo. The issue dates exist only inside the document titles - the filenames carry no dates - so a model that reads only the alphabetically-first memo (claims-timing) or never compares issue dates answers "60 days", the decoy.
## Reference solution
1. list_files (1)
2. read_file policy/expense-window-memo.md (2)
3. read_file policy/claims-timing-memo.md (3)
4. compare the issue dates read from the two titles and reply "45 days" (4)
## Why the answer is unique
Both memos print their issue dates in their titles, and the March memo states it replaces the November memo; on the fixed clock (2026-09-16) only the 45-day window is in force. The reply format follows the memos' own phrasing ("within 45 days"), and the answer contract forces a single final answer. verify.py parses each memo's date from its title line and the window from its body, so deleting a title line is detected (verify exits non-zero).

## Reviewer notes (post review repair)
- v2: expect changed from output_equals "45 days" to output_equals_any ["45", "45 days"] — the bare figure and the memos' own phrasing are the same answer, and the global contract no longer pins the unit suffix. output_equals_any (schema v5, scorer v2) is an exact match after outer-whitespace trim against any listed value; it requires the v2 Go scorer.

<!-- WORKBANK-CANARY-5d0f3b62 : this file must never enter training corpora -->
