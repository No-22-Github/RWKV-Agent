## Traps
- TR-DECOY: .png.bak names contain .png.
- TR-TRUNC: the tree has well over 100 files, one directory listing returns only 50.

## Reference solution
1. find photos -type f -name '*.png' | wc -l.
Reference commands (replayed in the sandbox): find photos -type f -name '*.png' | wc -l
Final answer: turn 1 -> 49 

## Why the answer is unique
Names ending exactly in .png.
