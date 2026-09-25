## Traps
- TR-AMBIG: the request names Hill Field, and the farm has two plots of that name, one
  at the north end and one at the south end. The north plot's rows give 117
  (38 + 44 + 35) and the south plot's give 54 (31 + 23); the sheet cannot say which
  plot the packhouse means, so the assistant has to ask.

## Reference solution
1. list_files: the workspace holds picking/packhouse-sheet-september.csv and README.md.
2. read_file picking/packhouse-sheet-september.csv: the plot column carries two Hill
   Field plots, so the request is not settled and the assistant asks which one is meant.
3. Turn 2 fixes the north plot. Add its rows: 38 + 44 + 35 = 117.

## Why the answer is unique
After the clarification only one Hill Field is in scope, and the sheet names the plot
on every row, so the north plot's three picking days are its own and add to 117. The
decoy 54 is the south plot's two rows; it is a real Hill Field figure, but it answers
for the other plot, and the request was settled on the north plot before the sum was
taken.

## Five alternative phrasings of the task
1. ruddleway farm september picking sheet
2. trays off hill field at ruddleway
3. ruddleway farm trays per plot
4. ruddleway hill field north plot trays
5. ruddleway farm packhouse tray count
