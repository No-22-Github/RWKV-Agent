## Traps
- TR-DECOY: exact answer 10.0.1.50; the loose reading (prefix match on path and any 4xx status) gives 10.0.1.5.
- TR-TRUNC: the file is 89KB and 1347 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$3=="/login" && $4==401 {c[$2]++} END{for (k in c) print c[k], k}' web/access.txt | sort -rn | head -1` -> 10.0.1.50
        the same pipeline prints the total (25) next to the name
Final answer: 10.0.1.50 had the most failed /login requests (25).

## Why the answer is unique
path and status are whole-value columns; the leader is ahead by at least three requests. The README (web/README.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. Top client IP by 401 responses on the /login endpoint?
2. In access.txt, which IP has the highest count of 401s for path /login?
3. Per web/README.md, which address failed /login the most?
4. Find the IP with the most /login requests answered by status 401.
5. Which IP is behind the largest number of 401 login failures?
