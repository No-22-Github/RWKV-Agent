## Traps
- None. The brief names the new figure and the settings file holds a single batch size, so there is nothing for a solver to weigh up.

## Reference solution
1. Read `config/invsync.json`, the settings the README points at: `batch_size` is 120.
2. Change that one value to 250 and leave the other keys alone. `tools/report_batch_size.py`, which the harness runs against the finished workspace, then prints 250.

## Why the answer is unique
The file carries exactly one batch size and the brief names exactly one target, so the expected end state is `batch_size: 250` and nothing else in the workspace suggests a different figure. The checker script reads the key back out of the file, so a solver cannot satisfy it by describing the change in its reply instead of making it. The answer is 250.
