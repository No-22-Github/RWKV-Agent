## Traps
- None declared. The scoring run adds a second monthly export the model never saw (expect.run.hidden_files, kept inside sales/), so a script that reads only the file it opened while exploring, or that hardcodes September's rows, misses the October day lines and fails the run check.

## Reference solution
1. Read bakes.py: its docstring fixes the layout.
2. Read sales/2026-09.csv to confirm the export columns.
3. Write bakes.py: sweep every sales/*.csv, skip each header, aggregate trays and loaves per product, print one line per product in alphabetical order, then the GRAND line.

## Why the answer is unique
The merged exports fix every number: Poppy Loaf 8 trays / 96 loaves, Rye Boule 9 / 108, Sesame Batard 7 / 84, Spelt Tin 3 / 30, Walnut Roll 6 / 72, so the sheet is exactly six lines ending GRAND,33,390. The layout is pinned by the docstring inside bakes.py, and the scoring run supplies sales/2026-10.csv, so a September-hardcoded script and a single-file script both miss the October lines and differ from the expected stdout.
