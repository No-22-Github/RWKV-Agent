# WORKBANK-CANARY-71c6ab2d : bank artifact, excluded from training corpora

## Traps
- TR-DEFN: two definitions run against intuition at once.
  (a) The statement's obvious number is the gross royalty - it is what the
  existing script prints and it is the first figure in each export row -
  while the payout the artist receives is defined only in payout_notes.md
  as the sum of gross_cents minus the sum of withheld_cents across the
  artist's tracks.
  (b) The switch is the wrong way round: the new flag, --gross, selects
  the behaviour the script has today, and a plain run - the invocation the
  scheduler already makes and the one the harness grades - has to change
  to the net figures. A solver that follows the intuitive shape and adds a
  --net flag while leaving the default alone leaves the graded plain run
  printing gross, and fails even though it built the net figures
  correctly. Both halves are pinned twice: the prompt says a plain run
  prints the payout and --gross keeps today's printout, and payout_notes.md
  says the same in finance's own words.
  The per-artist decoy figures are the gross totals Kestrel Nine 313400,
  Marisol Vega 339990, Ondine Choir 324040, Novlette Trio 102300 (total
  1079730); the correct net figures are Kestrel Nine 291400, Marisol
  Vega 316440, Novlette Trio 95000, Ondine Choir 301140 (total 1003980).
  On top, the harness writes in a second export the model never saw
  (statements/2026-late/q3-2026-encore.csv, one directory down), which
  adds Novlette Trio, so a hard-coded answer fails.
  trap_decoys is null (write/script case).

## Reference solution
1. read_file README.md - launch contract: run from the project root,
   statement exports under statements/ at unfixed depth (1)
2. read_file royalty_report.py - the existing gross-only statement and
   its <artist>,<cents> plus total layout (2)
3. read_file payout_notes.md - the net definition (gross less the sum of
   the per-track withheld reserves), that the default becomes net, and
   that --gross selects today's printout (3)
4. write_file royalty_report.py - add argument handling: a plain run
   prints gross minus withheld per artist, --gross reprints the gross
   totals, same layout and total line in both (4)

ref_calls = 4.

## Why the answer is unique
The payout notes fix the net definition exactly (gross_cents total less
withheld_cents total, per artist), the existing script fixes the layout
and order, and every amount is an integer number of cents, so the only
correct stdout for a plain run is the four net lines plus the total. The
hidden encore export makes the net figures depend on data the model never
saw, defeating a memorised statement.

## Grading note
expect.run grades the plain invocation (`python3 royalty_report.py`, no
args), because that is the run the scheduler makes and the run whose
behaviour the work changes. The --gross branch is specified in two places
but is not executed by the grader: RunExpectation carries one invocation,
so a script that prints the net figures on a plain run and mishandles
--gross still passes. v1 had the switch the intuitive way round (--net
selects net, default stays gross), which the expansion slot table for this
family rules out and which put this case's TR-DEFN on the same mechanism
as scr-0011's.

<!-- WORKBANK-CANARY-71c6ab2d : this file must never enter training corpora -->
