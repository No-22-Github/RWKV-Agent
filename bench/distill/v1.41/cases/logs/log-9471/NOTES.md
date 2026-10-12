## Traps
- Turn 1: exact answer 146; the loose reading (prefix match on unit and reason) gives 309.
- Turn 2: exact answer 129; the loose reading (unit prefix match includes api-gw-canary) gives 195.
- Turn 3: exact answer 12; the loose reading (reason prefix match includes oom-softlimit) gives 86.
- TR-TRUNC: the file is 81KB and 1282 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk '$2=="api-gw" && $3=="oom" {c++} END{print c+0}' svc/restarts.txt` -> 146
Turn 2: bash: `awk '$2=="api-gw" && $3=="deploy" {c++} END{print c+0}' svc/restarts.txt` -> 129
Turn 3: bash: `awk '$2=="worker" && $3=="oom" {a++} $2=="api-gw" && $3=="oom" {b++} END{d=a-b; if (d<0) d=-d; print d}' svc/restarts.txt` -> 12
Final answer: worker's oom count differs from api-gw's by 12.

## Why the answer is unique
unit and reason are whole-value columns. The README (svc/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. How many more or fewer oom restarts does worker have than api-gw? Give the absolute gap.
2. Count worker's oom restarts, then give me the difference to api-gw's oom count.
3. Absolute difference between the oom restart counts of worker and api-gw.
4. Compare oom restarts: worker versus api-gw, how big is the gap?
5. Work out worker's oom count and subtract api-gw's, ignoring the sign.
