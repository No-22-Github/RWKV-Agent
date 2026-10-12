## Traps
- TR-DECOY: exact answer 108; the loose reading (ip and result prefix match) gives 194.
- TR-TRUNC: the file is 86KB and 1277 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$3=="10.1.0.5" && $4=="FAILED" {print $2}' auth/logins.txt | sort -u | wc -l` -> 108
Final answer: 108 distinct users failed to log in from 10.1.0.5.

## Why the answer is unique
ip and result are whole-value columns; users repeat across rows and are de-duplicated. The README (auth/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of different users with a FAILED login from 10.1.0.5.
2. Rows with ip 10.1.0.5 and result FAILED: how many unique users?
3. Per auth/README.md, count the distinct users who failed from 10.1.0.5.
4. 10.1.0.50 and FAILED-LOCKED excluded, how many users failed from that address?
5. How many different accounts had a plain FAILED attempt from 10.1.0.5?
