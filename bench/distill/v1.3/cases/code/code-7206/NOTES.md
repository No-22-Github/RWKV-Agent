## Traps
- TR-DECOY: the name trim_history is echoed in a TODO comment (line 546), a log template string (line 971) and a second comment (line 1268) before the definition; taking the first hit answers the wrong line.
- TR-NEARNAME: the source also defines trim_history_locked (line 1113) with trim_history as a prefix. A definition is the exact `def trim_history(` line: 1686.

## Reference solution
1. Read README.md: it names moorline/history.py as the canonical source.
2. Search the name trim_history and read the line windows around the hits.
3. Rule out the comments, the log template and the locked twin; a definition is a `def` line with the exact name.
4. `def trim_history(` is at line 1686.

## Why the answer is unique
The README pins the canonical source; comments and log templates are not definitions, and trim_history_locked is a separate function whose name extends the target's. Exactly one `def trim_history(` line exists in the file: 1686.
