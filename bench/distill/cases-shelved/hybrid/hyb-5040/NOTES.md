## Traps
- TR-AMBIG: every load has two weights in the book, the loaded lorry (gross) and the
  empty one (tare), so the September intake can be read as 69280 kilograms or as 44460.
  Both readings are real sums over the same rows, so the assistant has to ask which
  weight the report is on.

## Reference solution
1. list_files: the workspace holds weighbridge/tip-book-september.csv and README.md.
2. read_file weighbridge/tip-book-september.csv: each load carries a loaded and an empty
   weight, so the request is not settled and the assistant asks which figure is meant.
3. Turn 2 settles on the net figure. Gross adds to 69280 and tare to 24820, so the
   material taken in is 69280 - 24820 = 44460.

## Why the answer is unique
After the clarification the report is on the net figure, and the README says the empty
lorry is weighed off on the way out, so what the site took in is each load's gross weight
less its tare. The six loads give 8360 + 7070 + 9500 + 5560 + 7760 + 6210 = 44460. The
decoy 69280 is the gross total; it is a real sum over the same book, but it includes the
vehicles rather than the material, and the report was settled on the net figure.

## Five alternative phrasings of the task
1. stanbrook tip september weighbridge book
2. how many kilograms did stanbrook tip take in september
3. stanbrook tip gross and tare weights
4. stanbrook tip net intake after vehicles
5. stanbrook tip september tonnage report
