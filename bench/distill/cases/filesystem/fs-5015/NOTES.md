## Traps
- None. The sheet carries the booked marks and the loaded marks on its own two lines, so the one mark that did not travel is a straight comparison.

## Reference solution
1. list_files (1): README.md and wharf-sheet.txt.
2. read_file wharf-sheet.txt (2): the booked line holds PL-4471, PL-4472, PL-4474, PL-4476, PL-4479 and PL-4480, the loaded line holds all of those except PL-4472, so the mark that stayed behind is PL-4472.

## Why the answer is unique
The booked line names six marks and the loaded line names five of them; five marks appear on both lines, so exactly one mark is booked and not loaded, PL-4472. The gate line records the time the van left and carries no mark, so it cannot supply a second candidate. The answer is PL-4472.
