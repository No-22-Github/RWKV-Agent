## Traps
- TR-DECOY: an archived copy of one file exists under archive/.
- TR-TRUNC: ~100 files so the listing hides the top-level ones.

## Reference solution
1. loop over REQUIRED.txt with test -f.
Reference commands (replayed in the sandbox): m=$(for f in $(cat deploy/REQUIRED.txt); do [ -f "$f" ] || echo $f; done); echo "$m"; echo "$m" | wc -l
Final answer: turn 1 -> 3 cron.yml cache.yml auth.yml

## Why the answer is unique
Presence is exact path.
