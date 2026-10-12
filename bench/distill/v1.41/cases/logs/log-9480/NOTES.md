## Traps
- Turn 1: exact answer 78; the loose reading (prefix match on ip and result) gives 124.
- Turn 2: exact answer 31; the loose reading (prefix match on ip and result, merging both failure kinds) gives 124.
- TR-TRUNC: the file is 92KB and 1281 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk '$3=="203.0.113.9" && $4=="FAIL" {print $2}' auth/events.txt | sort -u | wc -l` -> 78
Turn 2: bash: `awk '$3=="203.0.113.9" && $4=="FAIL-MFA" {print $2}' auth/events.txt | sort -u | wc -l` -> 31
Final answer: 31 different users had FAIL-MFA from 203.0.113.9.

## Why the answer is unique
ip and result are whole-value columns; users are de-duplicated. The README (auth/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of distinct users with result FAIL-MFA from 203.0.113.9.
2. How many unique users hit FAIL-MFA on that address?
3. Count each user once: FAIL-MFA events from IP 203.0.113.9 (not .90).
4. Per auth/README.md, how many different users show FAIL-MFA for 203.0.113.9?
5. De-duplicated user count for ip 203.0.113.9 and result FAIL-MFA.
