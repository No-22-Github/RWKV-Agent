# scr-8004 (p13 holdout, eval-only)

## Traps
- TR-DECOY: returns/archive/2026-08-w4.jsonl nests under the same directory and looks like more of the same data; the README scopes the count to top-level .jsonl files, so a recursive walk adds a `2026-08-w4.jsonl: 3` line (sorted first, before the week files) and fails. `trap_decoys` is null: the judged value is the script's stdout over visible plus hidden inputs, not a single fixture number.

## Reference solution
1. Read README.md for the counting rules and the output shape (ref call 1).
2. Read returns/week-1.jsonl and returns/week-2.jsonl (ref calls 2-3).
3. Write scripts/returns_count.py: for every top-level .jsonl in returns/, in filename order, print "<filename with extension>: <record count>" (ref call 4).

## Why the answer is unique
The README fixes both the scope (top-level .jsonl only) and the output shape (name with extension, colon, space, decimal count, sorted by filename), so exactly one stdout satisfies the case: one line per weekly file with its record count. The offline run copies a hidden returns/week-3.jsonl into the workspace before executing, so hard-coding week-1 and week-2 - or their counts - fails; only a script that implements the README's rules produces the expected three lines.
