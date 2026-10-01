## Traps
- TR-DUPROW: the notices sheet re-keys the Periwinkle claim, so Berth 14
  appears twice with the same summary and estimate; logging four claims is the
  trap, the log takes three.

## Reference solution
1. Read README.md: one line per claim in the shape `<date> <berth> "<vessel>" - <summary> - <estimate>`, each claim once in first-seen order, dated from the notices sheet.
2. Read notices/inspector-2026-09-28.txt and spot the re-keyed pair.
3. Read the existing log lines to match the style.
4. Append the Periwinkle, Heron and Sable lines under 2026-09-28.

## Why the answer is unique
The repeated notice matches its original in berth, vessel, summary and
estimate, and the README says a re-keyed notice is one claim logged once, so a
four-line append would double-book the same damage. The remaining three claims
carry all their fields on the sheet and the line shape is fixed by the
existing log, so the appended block is exactly three lines.
