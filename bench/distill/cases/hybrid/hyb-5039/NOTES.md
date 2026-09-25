## Traps
- TR-AMBIG: the book carries the same yield in two measures, litres and barrels, and the
  request asks for the quantity without saying which. The litres column adds to 6190 and
  the barrel column to 37; either is a real September figure, so the assistant has to ask
  which measure the report uses.

## Reference solution
1. list_files: the workspace holds press/presshouse-book-september.csv and README.md.
2. read_file press/presshouse-book-september.csv: two measure columns carry the same
   pressings, so the request is not settled and the assistant asks which one is wanted.
3. Turn 2 settles on litres. Add the volume_l column: 1450 + 980 + 1230 + 1660 + 870
   = 6190.

## Why the answer is unique
After the clarification the answer is in litres, and the book gives one litres figure per
pressing day, so the September yield is the sum of that column: 6190. The decoy 37 is the
barrel column; the README says the two columns are the same cider counted twice, so 37 is
that same September yield expressed in barrels and is not a second quantity, and the
report was settled on litres before the column was added.

## Five alternative phrasings of the task
1. whitlocke cider september press book
2. how much cider left the whitlocke press in september
3. whitlocke cider press house litres and barrels
4. whitlocke cider daily press yields
5. whitlocke cider september season report
