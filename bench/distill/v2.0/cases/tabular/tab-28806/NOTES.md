## Changelog
- v2: allow turn two to use a first-turn grouped result; first-turn query and exact values remain required.

## Traps
- None unless listed in tags; no test-bank source.

## Reference solution
Query 诊所/配药.csv, filter 柜台=东柜, aggregate sum 盒数: 181. Repeat for 西柜: 117 (or reuse an already returned grouped total in tab-8806). Recap with no calls.

## Why the answer is unique
Every row is a completed record; numbers are plain integers, equality filtering and sum/count are supported. Full-file reading is unnecessary.
