## Traps
- TR-SUPERSEDE: the ops memo of 2026-09-05 says 3200, the engineering bulletin
  of 2026-09-21 says 2000; the README says the later document governs, so
  applying 3200 is the trap.
- TR-DECOY: the yaml carries the install guide default 2400 in the value and
  repeats it in a trailing comment; changing the comment or the neighbouring
  keys is the second trap.

## Reference solution
1. Read README.md: where memos disagree, the later one governs.
2. Read both memos and compare dates: 2026-09-21 beats 2026-09-05, so 2000 governs.
3. Read config/playout.yaml.
4. Change stream's buffer_ms from 2400 to 2000, keeping the comment marker and every other line as it is.

## Why the answer is unique
The README fixes the tie-break rule and the bulletin is the later document, so
the ops memo's 3200 and the install guide's 2400 are both superseded
instructions, not settings. Only the buffer_ms line moves and its line shape
is preserved, so the edited file has exactly one possible content.
