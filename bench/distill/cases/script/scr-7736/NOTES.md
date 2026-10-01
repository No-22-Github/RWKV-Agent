## Traps
- TR-DUPROW: batches/2026-09.csv repeats CB-7102 and CB-7104 (and the hidden export repeats CB-7202); each batch_id is one batch (decoy: repeated batch rows double-counted)
- TR-HEADER: each export ends with a BATCH TOTAL closing line whose empty cells crash int(); the sheet has never carried it (decoy: the BATCH TOTAL closing line summed into the sheet)
- The scoring run also adds batches/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read logs/conch-2026-09.log: int(row["shell_kg"]) crashes on the BATCH TOTAL line.
2. Read batch_sheet.py and its docstring.
3. Read README.md: repeated batch rows are identical copies (one batch per batch_id) and the closing line never prints.
4. Read batches/2026-09.csv to confirm the repeats (CB-7102, CB-7104) and the BATCH TOTAL row.
5. Fix batch_sheet.py to skip the BATCH TOTAL line and count each batch_id once.

## Why the answer is unique
The README pins both rules: the BATCH TOTAL closing line never prints, and each batch_id is one batch. So 2026-09-02 prints 2,160 and the sheet ends TOTAL,8,641; leaving the closing line in crashes int(''), and counting the repeated CB-7102/CB-7104 rows inflates the batches and the kg. The hidden October export carries a repeat and its own closing line, so a partly fixed script fails there too.
