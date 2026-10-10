## Traps
- TR-HEADER: exports/rigging-w34.csv opens with two title lines and closes with a footer reading "2 fault warnings logged this week". Quoting the footer answers the breakdown question with a count of warnings; the hoist actually gave out on the BREAKDOWN row.

## Reference solution
1. Read README.md: columns start on the third line; the footer only counts FAULT warnings; BREAKDOWN marks the out-of-service entry.
2. Read exports/rigging-w34.csv, skipping the two title lines and the footer.
3. The BREAKDOWN row is 2026-08-19 11:15, hoist SL-2, brake pads seized; the CLEARED row at 15:00 shows it back in service after the swap and load test.

## Why the answer is unique
The footer "2 fault warnings" counts the two early brake warnings, which per README are warnings only — neither took the hoist out of service, and the event column separates them from the single BREAKDOWN row. That row is 2026-08-19 11:15 on hoist SL-2 with brake pads seized, and the CLEARED row closes the story at 15:00. Layout, the BREAKDOWN marker and the action text pin all three facts, so no second reading exists.
