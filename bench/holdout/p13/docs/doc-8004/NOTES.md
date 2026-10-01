# doc-8004 (p13 holdout, eval-only)

## Traps
- TR-DATEFMT: the minutes give the three due dates in three shapes - ISO (`2026-09-30`), `October 6` and `12 October` - while the August actions file fixes the output style as ISO with zero-padded month and day. Copying the dates verbatim produces `(due October 6)` / `(due 12 October)` and fails. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read minutes/staff-2026-09-24.md and take the three action items (ref call 1).
2. Read actions/2026-08-actions.md for the line layout and the date style (ref call 2).
3. Write actions/2026-09-actions.md with the three lines, dates normalized to 2026-09-30, 2026-10-06 and 2026-10-12 (ref call 3).

## Why the answer is unique
Owner, task wording and due date of every line are fixed by the minutes (the items are already phrased as `Owner: task`), and the layout `- Owner: task (due YYYY-MM-DD)` by the August file; the only transformation is date normalization, and exactly one ISO spelling exists for each date. The three contains needles pin each full line, and the `equals` pins keep the minutes and the August file untouched, so any rewording, reordering or verbatim date is a different end state.
