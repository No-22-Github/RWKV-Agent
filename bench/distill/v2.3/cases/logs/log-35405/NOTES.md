## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: search_text).

## Reference solution
bash: grep -c ' ERROR auth ' logs/gateway-edge-0914.log -> 13

## Why the answer is unique
Fields are timestamp, level, module, message; counted by level and module fields. Router lines mentioning an auth header are decoys for a loose grep.

Expected: 13
