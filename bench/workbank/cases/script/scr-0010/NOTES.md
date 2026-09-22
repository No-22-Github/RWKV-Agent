## Traps
- TR-NEARNAME: the traceback in README.md names `data/raw.csv`, a path that is
  no longer on disk. The extract that actually sits in `data/` is
  `data/raw_2026.csv` - the year suffix is the only difference, and the whole
  project tree holds exactly one `raw*` file, so the intended target cannot be
  confused with a second candidate. A repair that trusts the traceback path (or
  edits the module around it without opening the directory) keeps dying with the
  same FileNotFoundError and prints nothing; there is no stdout to compare, so a
  script that never locates the real extract scores zero. The unrelated
  `packing_rota.txt` and the `adjustments.csv` recount file are not near-names of
  the extract. trap_decoys is null (offline-run case; the decoy is the empty
  stdout of the still-crashing script).

## Reference solution
1. read_file README.md - the console capture; the job dies on `data/raw.csv`
   and both inputs live in the data directory (1)
2. read_file production_totals.py - the stale `EXTRACT` constant plus the
   recount pass over `adjustments.csv` that is already correct (2)
3. list_files the data directory - the only extract present is `raw_2026.csv` (3)
4. write_file production_totals.py - point `EXTRACT` at the extract that is
   actually there; leave the arithmetic, header and ordering untouched (4)

ref_calls = 4. A second input set overwrites `data/raw_2026.csv` with a later
month's extract inside the workspace copy before the offline run, so a repair
that hardcodes line totals or bypasses the file fails.

## Why the answer is unique
The extract columns and the signed recount file are fixed, the shipped
arithmetic, header and ascending line order are already correct, and the only
defect is the missing path, so the repaired script's byte-exact stdout is forced
to be:

```
line,cases
LINE-A1,715
LINE-B2,780
LINE-C3,592
total,2087
```

Every figure is an integer case count, and the single `raw_2026.csv` in the tree
makes the intended file unambiguous, so no second reading of the task survives.

<!-- WORKBANK-CANARY-c52e8a40 : this file must never enter training corpora -->
