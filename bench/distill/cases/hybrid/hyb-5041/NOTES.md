## Traps
- TR-AMBIG: the book carries the depot's own inspections and the coach inspections it
  does under a shared contract. Reading the fleet as the depot's own vehicles gives 13
  rows and reading it as the whole book gives 19, so the assistant has to ask which
  fleet the report covers.

## Reference solution
1. list_files: the workspace holds inspections/depot-book-september.csv and README.md.
2. read_file inspections/depot-book-september.csv: the fleet column carries own and
   partner rows, so the request is not settled and the assistant asks which fleet counts.
3. Turn 2 settles on the depot's own fleet. Its rows are HB-21 (three), HB-34 (three),
   HB-48 (three), HB-52 (two) and HB-57 (two), giving 13.

## Why the answer is unique
After the clarification the report covers the depot's own vehicles, and the book names
the fleet on every row, so the own rows are exactly the depot's inspections and there are
13 of them. The decoy 19 is the whole book, which includes the six Pennard Travel
inspections the README says are done under a separate contract; those are real rows, but
they are not the depot's own fleet, and the report was settled on the own fleet.

## Five alternative phrasings of the task
1. hollingbury depot september inspection book
2. how many inspections at hollingbury depot in september
3. hollingbury depot own fleet inspections
4. hollingbury depot inspection rows by fleet
5. hollingbury depot september fleet report
