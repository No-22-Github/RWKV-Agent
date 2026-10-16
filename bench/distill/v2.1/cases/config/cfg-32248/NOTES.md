## Traps
- TR-TRUNC: >100 files.

## Reference solution
1. grep -rl enabled: false | xargs grep -h name: | sed | sort > file.
Reference commands (replayed in the sandbox): grep -rl '^enabled: false' svc | xargs grep -h '^name:' | sed 's/name: //' | sort > svc/disabled.txt; wc -l < svc/disabled.txt; cat svc/disabled.txt
Final answer: turn 1 -> 53 

## Why the answer is unique
Names sorted bytewise.
