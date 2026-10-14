## Traps
- No file-writing tool is offered: the edit goes through the shell (sed), leaving everything else byte-identical.

## Reference solution
bash: sed -i '3s/timeout=30/timeout=60/' config/app.ini (line 3 is [server] timeout)

## Why the answer is unique
Only line 3 belongs to [server]; [client] has the same value and connect_timeout contains it. expect.files pins the full end state.
