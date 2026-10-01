## Traps
- TR-DECOY: the name open_gate is echoed outside call syntax — a TODO comment (line 508), a log template (line 895) and a second comment (line 1247); counting text occurrences overshoots.
- TR-NEARNAME: the twin gate_open_replay is defined once and called from its own site; its name extends open_gate as a substring, so a prefix search folds it in.

## Reference solution
1. Read README.md: the scope is sternway/ and a call site is a real call expression.
2. Search the name open_gate and read the line windows around the hits.
3. Keep only real call expressions; drop the definition, the comments, the log template and gate_open_replay.
4. The count is 13.

## Why the answer is unique
The README defines the scope and the notion of a call site; comments and log templates are not call expressions and gate_open_replay is a different function. The package holds exactly 13 call expressions of open_gate.
