## Traps
- TR-DUPROW: the round sheet re-keys the Door 2 alarm test, so it appears
  twice with the same result; logging four events is the trap, the log takes
  three.

## Reference solution
1. Read README.md: one line per event in the shape `<date> <event> - <result>`, each event once in first-seen order, dated from the round sheet.
2. Read sheets/round-2026-09-29.txt and spot the re-keyed pair.
3. Read the existing log lines to match the style.
4. Append the Door 2, Door 5 and Compressor 3 lines under 2026-09-29.

## Why the answer is unique
The repeated Door 2 row matches its original event and result, and the README
says a re-keyed event is one event logged once, so a four-line append would
record the same alarm test twice. The remaining three events carry their text
on the sheet and the line shape is fixed by the existing log, so the appended
block is exactly three lines.
