## Traps
- TR-NEARNAME: the manual calls the cabinet the "dough retarder" and a
  prover section already exists; naming the new section dough_retarder or
  merging the settings into prover is the trap. The README pins the short
  section name retarder.

## Reference solution
1. Read README.md: each cabinet is a top-level section; the new cabinet is named retarder with keys temp_c, humidity_pct, hold_hours, appended at the end in the two-space style.
2. Read config/ovens.yaml.
3. Append the retarder section with 4, 60 and 14, leaving the oven and prover sections byte-identical.

## Why the answer is unique
The README fixes the section name, the key set, the placement at the end of
the file and the indentation style, and the three values are given in the
request, so the appended block and the resulting file each have exactly one
possible content.
