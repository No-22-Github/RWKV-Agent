## Traps
None - L0 baseline of fam-script-stdlib-04. No trap is declared. The shipped
bin/reefer_rollup.py is complete and correct: it globs config/leg*.yaml, lets
PyYAML turn each file into a flat lane->pallets mapping, and prints the rollup
the scheduler mails. What stops it is the replay host, which runs scripts with
only the Python standard library available, so `import yaml` fails before any
print. A model that guesses the figures instead of rebuilding the script fails
the byte-exact stdout comparison, one that keeps the PyYAML import prints
nothing, and one that drops the glob for a hardcoded list of the two visible
legs loses a lane. The second input set (config/leg3.yaml, written into the
workspace copy before the script runs) adds the eastern lane and moves the
southern total, so totals lifted from the visible legs are wrong.

## Reference solution
1. read_file bin/reefer_rollup.py - the glob over config/leg*.yaml, the flat
   `lane: pallets` mapping it hands to PyYAML, and the printed layout (1)
2. read_file config/leg1.yaml - confirms the mapping shape the rewrite has to
   parse itself (2)
3. write_file bin/reefer_rollup.py - replace PyYAML with a small `lane: value`
   line parser behind the same glob, same ascending lane order and closing
   total (3)

ref_calls = 3. (Reading leg2.yaml as well is prudent but not required: the
replacement parser has to be format-general anyway, and the hidden leg3.yaml
is never visible during the session.)

## Why the answer is unique
The shipped script fixes the output: one `<lane>,<pallets>` line per lane in
ascending lane order, closed by `total,<sum>` over the lanes printed. The leg
files are flat mappings of whole pallets, so there is no nesting, typing or
rounding decision left open, and the hidden third leg has the same shape. The
one stdout the post-run workspace can produce is

  east,1290
  north,2235
  south,3190
  west,640
  total,7355

A rewrite that sums per file without pooling lanes prints north twice, one
that lets the last file read overwrite earlier lanes loses legs, and one that
keeps `import yaml` prints nothing at all; all three diverge line by line.

<!-- WORKBANK-CANARY-b6e3a1d7 : this file must never enter training corpora -->
