## Traps
- TR-DECOY: every file also has port= in [app] and [cache].
- TR-TRUNC: ~100 files.

## Reference solution
1. awk tracking the current section over all files.
Reference commands (replayed in the sandbox): awk '/^\[/{s=$0} s=="[db]" && /^port=/ && $0!="port=5432"{n++} END{print n}' tenants/*.ini
Final answer: turn 1 -> 22 

## Why the answer is unique
Section-aware match.
