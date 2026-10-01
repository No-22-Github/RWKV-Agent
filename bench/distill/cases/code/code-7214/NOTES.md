## Traps
- TR-CLAIM: the final CI SUMMARY line claims failed=0, but the README explains it was written before the failure parser ran; the body carries 3 distinct FAILED lines.

## Reference solution
1. Read README.md: the summary line predates the failure parser.
2. Search FAILED and read the line windows around the hits.
3. Collect the FAILED test ids in the run.
4. The count is 3.

## Why the answer is unique
The README disposes of the summary claim, so only FAILED lines count; each FAILED line names a distinct test. The count is 3.
