## Traps
- None. No trap tag is set: the board file carries one verdict line per check and one of them reads FAIL.

## Reference solution
1. Read board/lastrun.txt, the file the question names: it holds the verdict lines of the last run, one per check (call 1).
2. The only line starting with FAIL names seam_inspection, so that is the check that failed (call 1 as well).

## Why the answer is unique
The board file carries exactly one FAIL line, and the runner that writes it prints each check once, so the failing check is seam_inspection. The three PASS lines name the checks that passed, and no other file in the workspace records a verdict. The answer is seam_inspection.
