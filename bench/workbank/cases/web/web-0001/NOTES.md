## Traps
- None planted (L0 base case). All three fixture sources are consistent; the documentation page ranks first and carries the value in its option table. No stale sources, no dead links, and no snippet states a value, so there is no bait to fall for.

## Reference solution
1. web_search "oxcart configuration default batch size" (1)
2. web_fetch docs.oxcart.dev/en/stable/configuration/ — the ingest pipeline table lists batch_size with default 512 (2)
3. answer 512 (3)

## Why the answer is unique
The configuration reference is the vendor documentation page and its table marks batch_size with default 512. No other fixture entry states a batch_size default (the repo README and the benchmark article never mention one), so nothing contradicts it.

## Five alternative phrasings of the task
1. oxcart configuration default batch size
2. oxcart batch_size default value
3. what is the default batch size in oxcart
4. oxcart docs batch_size default
5. oxcart ingest batch_size out-of-the-box value

<!-- WORKBANK-CANARY-b4a17c93 : this file must never enter training corpora -->
