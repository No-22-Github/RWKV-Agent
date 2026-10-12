## Traps
- TR-DECOY: exact answer 32; the loose reading (env and result prefix match) gives 16.
- TR-TRUNC: the file is 89KB and 1248 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="prod" && $3=="OK" {c++; if (c==3) {print NR; exit}}' release/deploys.dat` -> 32
Final answer: The third successful prod deployment is on line 32.

## Why the answer is unique
env and result are whole-value columns and the line number counts from the first line. The README (release/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Line number of the 3rd prod deployment whose result is exactly OK.
2. Counting only env prod and result OK rows, where does the third one sit?
3. Per release/README.md, on which line is the third prod OK deployment?
4. prod-canary and OK-PARTIAL excluded, find the third match and give its line number.
5. Which line of deploys.dat is the third prod/OK row?
