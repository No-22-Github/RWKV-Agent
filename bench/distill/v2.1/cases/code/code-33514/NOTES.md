## Traps
TR-NEARNAME: nowEpoch; TR-DECOY: docs.js and the test.

## Reference solution
grep nowIso(; rename in 3 files.

## Why the answer is unique
logger.js and audit.js call it; the test and docs stay as they were.
Expected: lib/logger.js; lib/audit.js; nowUtc
