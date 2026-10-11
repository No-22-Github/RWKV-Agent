## Traps
- git is not installed (`command not found`, exit 127), so `git diff --no-index` cannot be used; plain `diff` per file pair works.
- TR-DECOY: db_host and cache_url differ by design, `pool_size=20` versus `pool_size = 20` is whitespace only, and the `# tuned` comment differs; only ttl_s has a different value.

## Reference solution
1. bash: `git diff --no-index configs/staging configs/prod` -> exit 127.
2. bash: `for f in app cache log; do diff configs/staging/$f.conf configs/prod/$f.conf; done`
Final answer: ttl_s is the setting whose value differs (300 in staging, 600 in prod); host/URL entries, the pool_size spacing and a comment aside.

## Why the answer is unique
After ignoring host/URL keys, comments and whitespace exactly one key differs.
