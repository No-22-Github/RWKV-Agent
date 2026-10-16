## Traps
- TR-DECOY: .mdx and .md.orig contain .md.
- TR-TRUNC: ~110 files.

## Reference solution
1. find -name '*.md' | wc -l.
2. find -name '*.md' -exec cat {} + | wc -l.
Reference commands (replayed in the sandbox): find docs -type f -name '*.md' -exec cat {} + | wc -l
Final answer: turn 1 -> 83 ; turn 2 -> 1597 

## Why the answer is unique
Exact extension; lines by newline count.
