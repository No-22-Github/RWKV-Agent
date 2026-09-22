## Traps
None: this is the L0 base of the family, a plain recursive sweep and
roll-up with no declared trap, so `tags.traps` is empty and
`trap_decoys` is `{}`. The one thing that can defeat a solver is stopping
the search at a single level: the seating drops sit at different depths
(`venues/<district>/<house>/admits.csv` and, for the late sync,
`venues/<district>/<house>/exports/admits.csv`) plus two hidden drops
one and two levels down. That is the family skeleton rather than a
declared trap, and the README states the whole-tree search as part of
the job, so no trap is claimed for it.

## Reference solution
1. list_files - project layout: README, the admissions_rollup.py stub,
   the venues tree, the unrelated ops note (1)
2. read_file README.md - drop-file columns (house, slot, seats_sold),
   the printed layout, ascending house order, whole-tree search (2)
3. write_file admissions_rollup.py - walk the tree for every
   admits.csv, sum seats_sold per house, print the `house,seats` lines
   and the total line (3)

ref_calls = 3.

## Why the answer is unique
Every house figure is a sum of integer seats_sold values, the layout and
ascending house order are pinned by the README, and the grand total is
defined as the sum of the printed house lines, so no rounding or
formatting choice is left open and the byte-exact stdout comparison has
one answer.

The scored stdout is the report over the workspace *including* the
hidden second drop set, which the harness writes inside the project tree
before the script runs:

    house,seats
    ARC-2,330
    BCN-4,300
    CVC-1,504
    LMP-7,383
    LUM-9,282
    ORC-3,310
    total,2109

`venues/eastport/lumen/admits.csv` adds a house the model never saw, and
`venues/riverside/civic/recheck/admits.csv` sits two levels below a house
folder and lifts CVC-1 from 431 to 504, so totals copied from the visible
tree fail while a recursive sweep passes. `files` still constrains the
answer: the visible drops alone fix ARC-2/BCN-4/LMP-7/ORC-3 and are read
by verify.py, so a corrupt fixture moves the expected stdout.
