## Traps
- TR-DECOY: canary in dev/staging also exists.
- TR-MISSING: some envs have no flags object.

## Reference solution
1. jq select .envs.prod.flags.canary==true | length.
Reference commands (replayed in the sandbox): jq '[.services[]|select(.envs.prod.flags.canary==true)]|length' deploy/services.json
Final answer: turn 1 -> 47 

## Why the answer is unique
Only prod env, canary strictly true.
