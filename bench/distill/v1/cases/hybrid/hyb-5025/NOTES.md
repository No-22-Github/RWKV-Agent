## Traps
- TR-AMBIG: the first request asks about the Hill flock, and two holdings keep one:
  Nethercote Farm and Withersfield Farm. Nethercote's biggest Hill flock day is 1610; the
  biggest day at Withersfield is 1745. The sheet cannot say which flock the review means, so
  the assistant has to ask before comparing days.

## Reference solution
1. list_files: the workspace holds collections/september-2026.csv and README.md.
2. read_file collections/september-2026.csv: two holdings each have a Hill flock, so the
   request is not yet settled and the assistant asks which one is meant.
3. Turn 2 fixes the Nethercote flock. Its Hill flock rows are 1480, 1610 and 1525, so
   the largest single day is 1610.

## Why the answer is unique
After the clarification one flock is in scope. The sheet writes one row for each day's
collection from one flock, so the biggest day is the largest of that flock's own rows.
Nethercote's Hill flock rows are 1480, 1610 and 1525, giving 1610; the decoy 1745 is
Withersfield's best Hill flock day, a real collection that belongs to the other holding, and
the review was settled on the Nethercote flock before the days were compared. The Valley
flock rows, the largest of which is 1440, are a different flock at the same holdings.

## Five alternative phrasings of the task
1. marshfield egg packing hill flock collection
2. best day for the nethercote hill flock
3. hill flock daily collections september
4. marshfield nethercote and withersfield hill flock
5. largest single day collection from the hill flock
