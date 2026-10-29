## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: replace_lines).

## Reference solution
read_file the 8-line file -> write_file the whole file back with only line 3 changed (MAX_CONNECTIONS_PER_IP stays 200).

## Why the answer is unique
expect.files pins the full end state; the _PER_IP line shares the value and a careless global replace would change it.

## Five alternative phrasings of the task
1. In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is.
2. Quick question: In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is.
3. In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is. (a short answer is fine)
4. Hi, In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is.
5. One more thing: In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is.
