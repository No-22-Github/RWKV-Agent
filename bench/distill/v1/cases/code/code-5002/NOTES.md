## Traps
- None. No trap tag is set: the caller names the function and the module it imports from, so the definition site follows from the first file the request points at.

## Reference solution
1. Read jobs/rotation.py, the module the nightly job runs: it binds rotate_shards with `from storage.shards import rotate_shards` (call 1).
2. Read storage/shards.py: the function is defined there, and storage/layout.py holds only the shard paths (call 2).

## Why the answer is unique
The job's import names storage.shards as the module the name comes from, and that module is the only one in the workspace with a `def rotate_shards(` line: storage/layout.py defines the path helper and imports nothing, and jobs/rotation.py only calls the name it imported. The answer is storage/shards.py.
