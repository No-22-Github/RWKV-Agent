## Traps
- No file-writing tool is offered: the edit goes through the shell (sed), leaving everything else byte-identical.

## Reference solution
bash: sed -i 's/v1\.2/v1.3/g' README.md

## Why the answer is unique
Three occurrences of v1.2; v1.1 stays. expect.files pins the full end state.
