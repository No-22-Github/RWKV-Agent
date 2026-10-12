## Traps
- TR-DECOY: exact answer 213; the loose match (prefix match, includes DENY-SOFT) gives 394.
- TR-TRUNC: the file is 63KB and 1319 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$4=="DENY" {print $2}' security/audit.txt | sort -u | wc -l` -> 213
Final answer: 213 distinct IPs were denied.

## Why the answer is unique
action is a whole-value column and IPs are de-duplicated. The README (security/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Count the unique source IPs that got DENY in audit.txt.
2. How many different IPs hit an actual DENY decision?
3. Number of distinct ips whose action is exactly DENY.
4. Per security/README.md, how many IP addresses were blocked?
5. De-duplicated count of IPs with a DENY line.
