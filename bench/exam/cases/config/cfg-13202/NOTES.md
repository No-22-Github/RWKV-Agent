## Traps
No declared trap. Turn 2's "prod has now" refers to the value after turn 1 (6), so staging must become 3. Half of the original 4 would give 2, which is what staging already has, so a model that ignores turn 1 leaves staging at 2.
Turn 1 is not judged separately (file state is only checked at the end).

## Reference solution
1. Replace prod `workers: 4` with `workers: 6`.
2. Replace staging `workers: 2` with `workers: 3`.

Final file:
```
service: orders-api
prod:
  region: eu-west-1
  workers: 6
  timeout_s: 30
staging:
  region: eu-west-1
  workers: 3
  timeout_s: 30
```

## Why the answer is unique
Prod = 6, staging = 6/2 = 3, everything else unchanged. Judged by a contains of the entire file without its final newline, so only a missing/extra final LF is tolerated.

EXAM-CANARY-3f1f542b
