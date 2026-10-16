## Traps
- TR-DECOY: tls.enabled and a commented line also contain enabled: true.
- TR-TRUNC: ~130 files.

## Reference solution
1. grep -rl '^enabled: true' services | wc -l.
2. xargs grep -h '^replicas:' | awk '$2>3' | wc -l.
Reference commands (replayed in the sandbox): grep -rl '^enabled: true' services | xargs grep -h '^replicas:' | awk '$2>3' | wc -l
Final answer: turn 1 -> 80 ; turn 2 -> 42 

## Why the answer is unique
Anchored top-level key.
