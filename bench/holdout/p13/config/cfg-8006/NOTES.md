# cfg-8006 (p13 holdout, eval-only)

## Traps
- TR-RULEFILE: the timeout value comes from the checklist's tier table, and kw-2203's roster row says 试点, which the checklist excepts from the tiering: pilot sites get 30 regardless of tier. Reading the row's tier as a C-level site (45) or copying the template's 60 without substituting produces the wrong file. The three source files are pinned byte-for-byte by `equals`. `trap_decoys` is null: the wrong outcome is a file state, not a single value.

## Reference solution
1. Read docs/网点接入清单.md for the field list, the file name rule and the timeout rule (ref call 1).
2. Read config/sites/kiosk-1.ini as the format template (ref call 2).
3. Read roster/2026Q4-openings.csv and take the kw-2203 row (ref call 3).
4. Write config/sites/kw-2203.ini with the five fields in the template's key order; timeout_seconds = 30 because the row is a pilot site (ref call 4).

## Why the answer is unique
The five field values are fixed by the roster row, the key spelling and order by the template file, and the one judgment call - the timeout - by the checklist's pilot exception (30, not the C-tier 45 and not the template's 60). The contains needles cover every line plus two adjacencies, so any other content, ordering or missing field is a different end state, and the `equals` pins keep the three sources untouched.
