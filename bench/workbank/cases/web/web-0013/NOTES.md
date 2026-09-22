## Traps
- None planted (L0 base case). All three fixture sources are consistent: the configuration reference ranks first and carries the value in its option table, the repository README points at that same reference, and the bakeoff article never states a setting value. No stale source, no dead link, and no snippet asserts a value, so there is no bait to fall for.

## Reference solution
1. web_search "cindermill configuration cache_ttl_hours" (1)
2. web_fetch docs.cindermill.dev/en/stable/reference/configuration/ — the cache table lists cache_ttl_hours with default 72 (2)
3. answer 72 (3)

## Why the answer is unique
The configuration reference is the project's own option table, and its cache_ttl_hours row carries a single default, 72. No other fixture entry states a value for cache_ttl_hours (the README and the bakeoff article never mention the option), so nothing contradicts it.

## Five alternative phrasings of the task
1. cindermill default cache_ttl_hours
2. cindermill cache_ttl_hours shipped value
3. what value does cindermill use for cache_ttl_hours by default
4. cindermill configuration reference cache_ttl_hours default
5. cindermill cache ttl hours default setting

<!-- WORKBANK-CANARY-7c4e9b31 : this file must never enter training corpora -->
