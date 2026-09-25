## Traps
- TR-AMBIG: the first request asks about Block 7, and both quarries in the log work a
  face of that name. Barrowcliff took out six loads from its Block 7 in September;
  Stonebank took out three from its own. The log cannot say which quarry the return
  covers, so the assistant has to ask before counting.

## Reference solution
1. list_files: the workspace holds extraction/september-2026.csv and README.md.
2. read_file extraction/september-2026.csv: the log carries Block 7 rows for two
   quarries, so the request is not yet settled and the assistant asks which face is
   meant.
3. Turn 2 fixes the Barrowcliff face. Count its Block 7 rows: 2, 7, 11, 17, 22 and 28
   September, six loads.

## Why the answer is unique
After the clarification one face is in scope. The log writes one row for each day a face
produced stone, so a load is counted once and a quarry's Block 7 rows are its own.
Barrowcliff's six rows give 6; the decoy 3 is Stonebank's three Block 7 rows, a real
count of a different face, and the request was settled on Barrowcliff before the count
was taken. The four rows under Block 4 belong to faces with other names.

## Five alternative phrasings of the task
1. barrowcliff and stonebank block 7 loads september
2. how many loads came out of block 7
3. quarry extraction log september block 7
4. barrowcliff quarry block 7 wagon loads
5. block 7 loads at both quarries
