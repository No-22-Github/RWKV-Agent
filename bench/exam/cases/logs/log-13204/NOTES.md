## Traps
Corrected scope. With the fixed clock 2026-09-16, yesterday is 09-15 (billing: 4 server errors vs search 2, orders 1) and the day before yesterday is 09-14 (search: 3 vs orders 2, billing 1). The 09-16 file is a decoy for "today" readings (inventory 5). The turn-2 answer must be search and must lead with it (first line), not repeat billing as the conclusion.
Turn 1 expects billing.
Scoring note (r1 finding): a plain output_excludes on billing wrongly failed a correct reply whose table listed billing's count of 1. Replaced with output_first_line_contains_any so the conclusion must lead with the new answer.

## Reference solution
1. Count status 5xx per service in access-2026-09-15.log -> billing 4.
2. Re-count for access-2026-09-14.log -> search 3.

## Why the answer is unique
The three files are named by date; counts are unambiguous and top-1 has no tie in either day.

EXAM-CANARY-f8a2a88a
