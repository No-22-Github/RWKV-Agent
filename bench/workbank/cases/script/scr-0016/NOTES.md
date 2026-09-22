## Traps
- TR-TRUNC: the spool holds 205 tally files, and the workspace listing tool
  answers with at most 200 entries by default, flagging the answer as cut
  short. Those 200 entries are README.md, spec.md, the spool directory and
  then spool/lot-0001.* through spool/lot-0197.*; the walk only reaches
  tally.py after the whole spool has been traversed, so that is cut off too,
  and everything from lot-0198 onwards never appears in the listing a model is
  shown. Building the rollup from what that listing exposed gives
  shipped_lots,167 / shipped_units,85099 / held_lots,24 / held_units,10379
  instead of shipped_lots,182 / shipped_units,91799 / held_lots,28 /
  held_units,11616. The second input set (twelve lots under
  spool/2026-09/w39/, three directories below the root) is not in the workspace
  the model works in - the harness writes it only into the copy the graded run
  executes against - so it can be neither listed nor hard-coded. At grading
  time it is reachable only by a recursive walk: a glob of spool/* prints
  shipped_lots,172 / shipped_units,87186 / held_lots,26 / held_units,11166
  instead of the correct rollup. (The default listing walk stops at max_depth 3
  and would not reach that folder either; the 200-entry cut is what hides the
  tail of the visible spool, not the hidden set.) The README states that tallies land in
  whatever subfolder the controller is configured for, and the hidden set sits
  inside the project tree, so both os.getcwd() and Path(__file__).parent reach
  it.
- TR-RULEFILE: which suffixes count, and how, lives only in spec.md, and the
  data hits every clause. Counting every tally file as shipped (ignoring the
  class split) gives shipped_lots,210 with held_lots,0 / held_units,0 and
  shipped_units,103415. Reading `.rework` as a QA hold because its name says
  held - instead of applying the spec's clause that reworked lots are released
  by the time the rollup runs - gives shipped_lots,172 / shipped_units,86881 /
  held_lots,38 / held_units,16534. The seven scratch files (`.tmp`, one of them
  past the listing limit) hold notes rather than units, so a rollup that
  treats every file in the spool as a tally also fails. trap_decoys is null for
  both traps (the case is scored on the script's stdout).

## Reference solution
1. read_file README.md - where tallies land, the four printed figures, and
   that spec.md carries the classes (1)
2. read_file spec.md - the three suffixes, the separate held figures, and the
   clause that reworked lots count as shipped (2)
3. read_file spool/lot-0001.ship - the one-line tally shape (3)
4. list_files - survey the spool; the answer comes back cut at the entry limit
   with the flag set, which is why the rebuild has to walk the tree itself (4)
5. write_file tally.py - walk the spool tree from the project root, classify by
   suffix per spec.md, sum units per class, print the four lines (5)

ref_calls = 5.

## Why the answer is unique
spec.md fixes the suffix classes, states that held figures are never folded
into shipped ones, and states that reworked lots count as shipped, so neither
the class split nor the treatment of `.rework` is left to the reader's
intuition; README.md fixes the four line labels and their order, and every
tally file holds exactly one integer, so no parsing decision is open. The one
stdout the post-run workspace can produce is

  shipped_lots,182
  shipped_units,91799
  held_lots,28
  held_units,11616

The listing-limited reading gives 167/85099/24/10379, folding held into
shipped gives 210/103415/0/0, moving rework to held gives 172/86881/38/16534,
and a non-recursive glob loses the twelve hidden September lots; each diverges
from the expected stdout line by line.

<!-- WORKBANK-CANARY-e708b3c5 : this file must never enter training corpora -->
