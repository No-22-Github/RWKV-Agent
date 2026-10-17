## Traps
TR-DECOY: timeout_seconds appears three times in prod.yaml and in staging.

## Reference solution
grep -n; pick the one under liveness.

## Why the answer is unique
prod.yaml line 17 value 15.
Expected: deploy/prod.yaml; 17; 15
