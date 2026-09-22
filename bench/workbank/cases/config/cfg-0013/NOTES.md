## Traps
None. This is the L0 baseline of the family: the work order names one
setting and one new value, and only that value may change.

## Reference solution
1. read changes/WO-5580.txt — the approved value is 960 for
   spool-writer's max_batch_records.
2. read services/spool-writer.yaml — max_batch_records sits under runtime
   and carries a trailing comment on the same line.
3. Replace the number 480 with 960 on that line, leaving the indentation
   and the comment intact; no other file changes. The graded end state is
   `  max_batch_records: 960   # raised 2026-08-14 for the quarter-end backlog`
   inside services/spool-writer.yaml, with changes/WO-5580.txt,
   environments/qa.env, README.md and ops/squad-roster.md byte-identical.

## Why the answer is unique
WO-5580 names exactly one setting and one value (960), and
max_batch_records occurs exactly once in the workspace, so there is a
single line to change and a single resulting file state. The README
requires the surrounding comments and indentation to survive, which pins
the rest of the line. 960 is the same width as the 480 it replaces, so
preserving the spacing and preserving the comment's column are the same
edit and the graded line is not ambiguous.

## Grading note
expect.files pins every line of services/spool-writer.yaml, each with its
own indentation, rather than the three bare substrings v1 used. Bare
substrings passed states in which the work order had not taken effect: the
original `  max_batch_records: 480 …` line left alone and a top-level
`max_batch_records: 960` appended below it is a different key (the graded
one is nested under `runtime:`), so the service would still run at 480.
The indented needles reject that, and they also reject a de-indented file,
a moved or dropped comment, and the deletion of any other line.

Residual: `contains` cannot express "and nothing else", so a file that
keeps the graded line and additionally appends a duplicate indented key
still passes. Closing that needs an `excludes` (or a normalizing `equals`)
on FileExpectation, which is a harness change and is filed for the tools
round; byte-exact `equals` is not the fix, because it would fail a model
whose write_file call omits the fixture's trailing newline.

<!-- WORKBANK-CANARY-7d21b4ea : this file must never enter training corpora -->
