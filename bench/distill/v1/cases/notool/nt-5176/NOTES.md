## Traps
- TR-NOTOOLNEED: ops/cleanup-cards.tsv, README.md and notes/run-notes.txt are props. Trap behaviour is a property of the shell, so no file has to be read. The near-miss decoy `trap 'rm -f /var/tmp/fare-export.work' ERR` fires only after a command fails, so the scratch file survives a run that reaches its last command, which is the case the question names first.

## Reference solution
1. Answer from the shell: the condition that covers both a normal end and an early exit is `EXIT`, and `rm -f` keeps the handler silent when the file was never created.
2. Reply with `trap 'rm -f /var/tmp/fare-export.work' EXIT`.

## Why the answer is unique
The question names two ways the script stops, a normal end and an early exit after a failed command, and `EXIT` is the trap condition that runs on both while `ERR` runs only on the second. The handler cannot be a plain `rm` without `-f`, because the question says the file may never have been created and the cleanup must not report an error. `ERR` cannot be a reading of the question: a run that reaches its last command would keep the scratch file.
