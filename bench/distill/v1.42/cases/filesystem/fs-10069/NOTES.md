## Traps
- TR-DECOY: globbing '*.gz' (bare .gz files counted, .tgz missed) gives 119; the README's rule gives 114.
- 206 files in nested folders under dist/, so counting by listing is not practical.

## Reference solution
1. bash: `find dist -type f \( -name '*.tar.gz' -o -name '*.tgz' \) | wc -l` -> 114
Final answer: 114 tarballs (.tar.gz plus .tgz; plain .gz and .sha256 files excluded).

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
