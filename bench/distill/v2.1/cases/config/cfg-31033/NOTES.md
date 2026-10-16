## Traps
- TR-DECOY: archive-old.env also holds 8080 and must stay; prod.env has two occurrences.
- 4 file(s) change, 1 stay byte-identical.

## Reference solution
1. grep 8080 across ops
2. edit each of the four files
3. grep again to confirm only archive-old.env keeps 8080

## Why the answer is unique
Four files change, archive stays.
Final answer should mention: 9090; archive-old.env
