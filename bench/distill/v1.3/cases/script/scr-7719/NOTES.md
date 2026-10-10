## Traps
- TR-DECOY: the status column holds open and reopened side by side, and the substring "open" sits inside "reopened". A contains-check counts the four reopened tickets too (Priya 4 / Wren 4) although the docstring says a reopened item is off the bench.
- TR-DUPROW: the feed re-posts tickets now and then with identical rows - MC-3303 in September (reopened), MC-3404 once October lands (open). The docstring says count each ticket once; counting the October re-post twice puts the TOTAL at 6 instead of 5.

## Reference solution
1. Read queue.py: its docstring fixes the re-post rule and what each status means.
2. Read tickets/2026-09.csv: MC-3303 appears twice and reopened sits beside open.
3. Read README.md: the re-posted rows are identical.
4. Add the --open flag: dedupe by ticket_id, count only status exactly "open", keep the layout; the no-flag behavior stays exactly as it is.

## Why the answer is unique
With one row per ticket and only exact "open" counted, the merged run (the scoring run adds tickets/2026-10.csv) prints exactly Priya Shah,3 / Wren Okafor,2 and TOTAL,5. The docstring states that reopened items are off the bench and that re-posted tickets count once, so both the substring reading and the twice-counted MC-3404 contradict the record the ticket system itself keeps; the no-flag behavior is pinned byte-identical by the prompt.
