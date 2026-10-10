## Traps
- TR-DECOY: coolroom/labels.py imports freeze_run from the chill store and never calls it, so a reader who takes the first module that names the helper answers coolroom/labels.py instead of the module that holds the call.

## Reference solution
1. Read store/chill.py: the module defines freeze_run and calls nothing (call 1).
2. Read coolroom/freezer.py: it takes the helper as freeze and calls it inside run_day() (call 2).
3. Read coolroom/labels.py: it imports the helper and only formats a label, so it holds no call (call 3). The module that calls freeze_run is coolroom/freezer.py.

## Why the answer is unique
The decoy is coolroom/labels.py, and it is wrong because an import binds a name without calling it: labels.py never passes a crate, so its only mention of the helper is the import line. coolroom/freezer.py binds the same helper under the name freeze and passes a crate to it, which is a real call, and no other module in the workspace names the helper at all. The answer is coolroom/freezer.py.
