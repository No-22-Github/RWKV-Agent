## Traps
- None unless listed in tags; no test-bank source.

## Reference solution
Query 仓储/收货.csv, filter zone=南仓, aggregate sum crates: 7330. Repeat for 北仓: 3531 (or reuse an already returned grouped total in tab-8806). Recap with no calls.

## Why the answer is unique
Every row is a completed record; numbers are plain integers, equality filtering and sum/count are supported. Full-file reading is unnecessary.
