## Traps
- TR-AMBIG: the request names Bramble while treks/march-2026.csv holds two candidates, Little Bramble and Big Bramble. Reading it as Big Bramble gives 13; the request was settled on Little Bramble, giving 16.5 (from treks/march-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names Bramble but the workspace holds two candidates, Little Bramble and Big Bramble, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds treks/march-2026.csv and README.md.
3. read treks/march-2026.csv and take the total of the hours column for Little Bramble: 16.5.

## Why the answer is unique
The decoy 13 belongs to Big Bramble; it answers a different candidate, and the request was settled on Little Bramble before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 16.5.

## Five alternative phrasings of the task
1. dalefoot trekking centre bramble hours march 2026
2. treks out with big bramble and little bramble
3. hours under saddle per horse dalefoot
4. march farrier review hours bramble
5. trekking hours logged for the brambles
