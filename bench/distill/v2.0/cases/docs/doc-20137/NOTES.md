## Traps
- No file-writing tool is offered: the edit goes through the shell (sed), leaving everything else byte-identical.

## Reference solution
bash: printf ... >> CHANGELOG.md

## Why the answer is unique
The new text is given verbatim; the old content is kept. expect.files pins the full end state.
