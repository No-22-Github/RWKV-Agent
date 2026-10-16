## Traps
- TR-DECOY: three *_SAMPLE_RATE=0.1 lines.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file
2. replace line 11
3. read back

## Why the answer is unique
Only TRACE_SAMPLE_RATE=0.5.
Final answer should mention: TRACE_SAMPLE_RATE=0.5; 0.2; 0.5; 0.1
