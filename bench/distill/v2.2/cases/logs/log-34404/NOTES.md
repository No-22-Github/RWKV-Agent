## Traps
An earlier, finished job imp-3309 is a decoy; the job running at the OOM is imp-4471, started four lines earlier.

## Reference solution
grep -n OutOfMemoryError | head -1 -> line 2125; read_file path=etl.log start_line=2118 end_line=2126.

## Why the answer is unique
The job started right before the first OOM is imp-4471. Expected answer per turn: imp-4471.
