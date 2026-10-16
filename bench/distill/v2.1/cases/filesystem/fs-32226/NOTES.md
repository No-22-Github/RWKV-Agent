## Traps
- TR-DECOY: ORDER-77310 is a longer reference in another file.
- TR-TRUNC: 100+ files.

## Reference solution
1. grep -rnE with a non-digit boundary.
Reference commands (replayed in the sandbox): grep -rnE 'ORDER-7731($|[^0-9])' exports
Final answer: turn 1 -> 4 batch-085.txt

## Why the answer is unique
Boundary-checked match appears once.
