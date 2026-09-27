## Traps
- TR-MISSING: the delay_code column mixes real codes with NA, dashes and empty cells. The readme
  defines every non-code marker as an on-time delivery, so the delayed count is 6; a reader who
  counts every row with anything in the column reports 16.

## Reference solution
1. List the workspace: the March manifest, a readme and an unrelated depot note.
2. Read README.md: only W1, V2 and T3 are delays; dash, NA and empty all mean on time.
3. Read depot/manifest_2026-03.csv and count rows carrying one of those three codes: 6.

## Why the answer is unique
The readme assigns a meaning to every value the column can hold and reserves delay for the three
codes, so the count is settled by the file itself. Counting NA or dash rows as delays asserts the
opposite of what the readme states, and that reading produces the decoy 16. The answer is 6.
