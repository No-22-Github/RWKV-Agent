## Traps
- TR-TRUNC: the spool holds 212 scan-event files, and the workspace listing
  tool answers with at most 200 entries by default, flagging the result it
  returns as cut short. In this tree those 200 entries are the three root files
  plus the spool directory and then spool/b0001.csv through spool/b0196.csv, so
  everything from spool/b0197.csv onwards never appears in the listing a model
  is shown. A rollup built from what that listing exposed prints
  ok,142 / late,26 / void,28 / total,196 instead of ok,155 / late,32 / void,35
  / total,222. The second input set (ten further events under
  spool/2026-09/w38/, three directories below the root) is not in the
  workspace the model works in at all - the harness writes it only into the
  copy the graded run executes against - so it cannot be listed, read or
  hard-coded. Two separate things follow. Nothing the model can see tells it
  the counts, so hard-coded counts fail. And at grading time the set sits
  three directories down, so a script that globs only spool/*.csv rather than
  walking the tree prints ok,149 / late,30 / void,33 / total,212 instead of
  the correct rollup. (The default listing walk stops at max_depth 3 and would
  not reach that folder either; the 200-entry cut is what hides the tail of
  the visible spool, not the hidden set.) The
  README states that events land in whatever subfolder the service is
  configured for, so the recursive sweep is the stated contract and not an
  unstated idiom, and the hidden set sits inside the project tree so both
  os.getcwd() and Path(__file__).parent reach it. trap_decoys is null (the case
  is scored on the script's stdout).

## Reference solution
1. read_file README.md - one line per event, the outcome vocabulary, the
   printed layout, and that events land in subfolders (1)
2. read_file rollup.py - the stub that has to be replaced before the job can
   print anything (2)
3. list_files - survey the spool; the answer comes back cut at the entry limit
   with the flag set, which is exactly why the rebuild must walk the tree
   itself instead of enumerating what the listing showed (3)
4. write_file rollup.py - os.walk the spool tree from the project root, count
   ok/late/void, print the four lines (4)

ref_calls = 4.

## Why the answer is unique
README.md fixes the outcome vocabulary, the line layout and the order of the
lines, and every event file holds exactly one `<parcel_id>,<outcome>` line, so
there is no field-splitting or which-column decision left open. Counting is
exact and the spool has no duplicate or unscannable rows. The one stdout the
post-run workspace can produce is

  ok,155
  late,32
  void,35
  total,222

The listing-limited reading gives ok,142 / late,26 / void,28 / total,196, a
non-recursive glob loses the ten hidden September events, and a hardcoded set
loses them as well; each diverges from the expected stdout line by line.

<!-- WORKBANK-CANARY-d21a7f63 : this file must never enter training corpora -->
