## Traps
- TR-DUPROW: the queue manager re-sent 6 flood alarms unchanged, so the window holds 22 flood ERROR lines over 16 jobs. Counting lines answers 22; merging re-sends by job id answers 16.

## Reference solution
1. Read README.md: line grammar and the re-send rule.
2. Search 'queue flood' and read the line windows around the hits.
3. Keep ERROR lines from queue-mgr whose timestamps fall inside 23:10:00-23:40:00.
4. Merge re-sends by job id; the distinct count is 16.

## Why the answer is unique
Re-sent lines repeat every field of their original, so the README's rule makes them one job; the level and message opening admit only flood ERRORs and the window edges are exact. The distinct count is 16.
