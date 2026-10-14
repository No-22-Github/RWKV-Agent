## Traps
- No file-writing tool is offered: the edit goes through the shell (sed), leaving everything else byte-identical.

## Reference solution
Turn 1: sed value. Turn 2: sed -i '/^DEBUG_SQL=/d'.

## Why the answer is unique
Two sequential edits; the end state is fixed. expect.files pins the full end state.
