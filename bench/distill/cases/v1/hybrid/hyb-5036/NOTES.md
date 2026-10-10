## Traps
- TR-AMBIG: the request names Pellow's bench while the firm has two technicians called
  Pellow, Dawn and Ivan. Dawn's rows give 46 (14 + 17 + 15) and Ivan's give 29
  (11 + 8 + 10); the book alone cannot say which bench the claim means, so the
  assistant has to ask before it adds anything up.

## Reference solution
1. list_files: the workspace holds rewinds/bench-book-september.csv and README.md.
2. read_file rewinds/bench-book-september.csv: the technician column carries two
   Pellows, so the request is not yet settled and the assistant asks which one is meant.
3. Turn 2 fixes Dawn Pellow. Add her rows: 14 + 17 + 15 = 46.

## Why the answer is unique
After the clarification only one of the two Pellows is in scope. The book writes one
row per technician per day and names the technician, so Dawn Pellow's rows are exactly
her three days on the bench and their units add to 46. The decoy 29 is Ivan Pellow's
three rows; it is a real figure from the same book, but it answers for the other
technician, and the request was settled on Dawn before the sum was taken.

## Five alternative phrasings of the task
1. pennerley rewinds september bench book
2. units off pellow's bench at pennerley
3. pennerley rewinds daily units per technician
4. how many units did dawn pellow rewind
5. pennerley rewinds september claim
