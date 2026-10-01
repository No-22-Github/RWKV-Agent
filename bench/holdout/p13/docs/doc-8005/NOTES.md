# doc-8005 (p13 holdout, eval-only)

## Traps
- TR-DECOY: two handover logs sit side by side; the entry belongs in logs/handoff-2026-09.txt, the current month the prompt names. Appending to the August log fails its `equals` pin and leaves the September file without the entry; creating a third file fails too. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read logs/handoff-2026-09.txt for the entry format and its last line (ref call 1).
2. Append one line in the same shape - date, shift, name, colon, what happened, ticket number - as the file's last line (ref call 2).

## Why the answer is unique
The prompt fixes date, shift, name, place, event and ticket number, and the existing entries fix the line shape, so the appended line is determined up to punctuation that the needles tolerate. The end-anchor needle requires the new line to start immediately after the 2026-09-27 entry (no blank line in between, no middle insert), and the August log is pinned byte-for-byte.
