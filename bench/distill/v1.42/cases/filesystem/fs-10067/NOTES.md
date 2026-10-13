## Traps
- TR-DECOY: matching '*.log*' (rotations and locks too) gives 205; the README's rule gives 87.
- 231 files in nested folders under var/, so counting by listing is not practical.

## Reference solution
1. bash: `find var -type f -name '*.log' | wc -l` -> 87
Final answer: There are 87 live .log files under var/ (rotated .log.gz/.log.N and .lock files excluded).

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
