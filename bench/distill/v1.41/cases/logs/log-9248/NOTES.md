## Traps
- TR-DECOY: exact answer 188; the loose match (any 4xx status) gives 264.
- TR-MULTISRC: 3 files; the first file alone gives 80.

## Reference solution
Turn 1: bash: `cat gw/*.txt | awk '$4==429 {print $2}' | sort -u | wc -l` -> 188
Final answer: 188 distinct tenants were rate limited.

## Why the answer is unique
status 429 is matched exactly; tenants are de-duplicated across files. The README (gw/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of unique tenants that were rate limited (429) on any edge node?
2. Count distinct tenant ids with at least one 429 in gw/.
3. Across edge-a, edge-b and edge-c, how many tenants hit the rate limit?
4. How many tenants appear with status 429, de-duplicated?
5. Per gw/README.md, how many different tenants were throttled?
