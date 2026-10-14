## Traps
- None. Every row carries its own label, training row or boat move, so counting the crewed outings is a single pass over the register.

## Reference solution
1. list_files (1): README.md and boathouse-register.txt.
2. read_file boathouse-register.txt (2): rows 219, 221, 222, 224, 225, 227, 228, 229, 231, 232, 233 and 234 read training row, so the count is 12.

## Why the answer is unique
The register holds sixteen rows, 219 to 234 inclusive, and each row is labelled either training row or boat move. Twelve rows read training row and the remaining four read boat move, so the crewed outings are 12. No row carries both labels and no row is counted twice, so the answer is 12.
