## Traps
- TR-DECOY: across all branches a different job fails most.

## Reference solution
1. jq -r failed main runs | sort | uniq -c | sort -rn.
2. Sum duration_s of that job's failed main runs.
Reference commands (replayed in the sandbox): jq -s 'map(select(.branch=="main" and .result=="failure"))|group_by(.job)|map({j:.[0].job,n:length,s:(map(.duration_s)|add)})|sort_by(-.n)|.[0].s' ci/runs.jsonl
Final answer: turn 1 -> 11 deploy-stg; turn 2 -> 12182 

## Why the answer is unique
Branch and result are exact strings; winner has a clear margin.
