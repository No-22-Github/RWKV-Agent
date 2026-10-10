## Traps
- None. The two kinds of visit are labelled on every row, so counting one kind is a single pass over one file.

## Reference solution
1. list_files (1): season-register.txt and README.md.
2. read_file season-register.txt (2): the first row of the register is kept and rows 141, 143, 145, 147, 149, 151 and 153 are marked extraction, so the count is 7.

## Why the answer is unique
Every row of the register carries exactly one visit label, inspection or extraction, and the visits are 141 to 153 inclusive, thirteen rows in all. Rows 141, 143, 145, 147, 149, 151 and 153 read extraction, which is 7 rows; the remaining six rows read inspection. No row carries both labels and no extraction visit is recorded outside the register, so the count of extraction visits is 7.
