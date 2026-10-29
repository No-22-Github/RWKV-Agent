## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: datetime).

## Reference solution
read_file the terms -> start 2026-03-14; bash: date -d @$(( $(date -d 2026-03-14 +%s) + 100*86400 )) +%F -> 2026-06-22 (the sandbox date rejects '+ 100 days'; counting by hand also works).

## Why the answer is unique
Signed date and end date are decoys.

Expected: 2026-06-22

## Five alternative phrasings of the task
1. What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD.
2. Quick question: What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD.
3. What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD. (a short answer is fine)
4. Hi, What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD.
5. One more thing: What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD.
