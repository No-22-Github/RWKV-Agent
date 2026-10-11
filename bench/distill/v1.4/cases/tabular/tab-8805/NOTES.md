## Changelog
- v2: clarify reply-only recap and numeric spelling; tool restrictions and all result values unchanged.

## Traps
- None unless listed in tags; no test-bank source.

## Reference solution
Query harbor/checks.csv, filter berth=Reed, aggregate count: 39. Repeat for Slate: 20 (or reuse an already returned grouped total in tab-8806). Recap with no calls.

## Why the answer is unique
Every row is a completed record; numbers are plain integers, equality filtering and sum/count are supported. Full-file reading is unnecessary.
