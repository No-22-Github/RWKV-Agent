## Traps
- TR-DECOY: worker/beat.py 底部留着一行注释掉的 purge_cache 调用，按文本搜索会多算一处、答成三个调用方。 A careless pass reports `3`.

## Reference solution
1. Read worker/jobs.py to locate the definition.
2. Read worker/api.py and worker/beat.py for call sites, treating the commented v1 line as dead text.
3. List the calling functions and the defining file.

## Why the answer is unique
The commented line in beat.py is dead text with its retirement year attached, so the live callers are purge_endpoint in api.py and nightly_sweep in beat.py, and the definition sits in jobs.py. No other worker file references purge_cache, which fixes the caller list at two.
