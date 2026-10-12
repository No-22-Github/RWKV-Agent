## Traps
- TR-DECOY: a commented-out CACHE_TTL_SECONDS=60 line in the same file and 120 in prod.env.example.

## Reference solution
1. read_file config/prod.env
Final answer: 300 seconds (the commented 60 and the example file's 120 are not in effect).

## Why the answer is unique
The user names config/prod.env; only its live line holds the answer. A commented-out 60 and the .example file's 120 are not live.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash.

## Five alternative phrasings of the task
1. In config/prod.env, what is CACHE_TTL_SECONDS set to?
2. How long (seconds) is the cache kept according to config/prod.env?
3. Check config/prod.env for the effective cache TTL.
4. What value of CACHE_TTL_SECONDS is live in config/prod.env?
5. config/prod.env: what's the cache time-to-live in seconds?
