## Traps
- TR-MULTISRC: the journals live in two files. Reading only morvane-oven-a.log (the file that sorts first) finds its first ERROR at 03:15 and answers morvane-oven-a, but morvane-oven-b.log records an ERROR at 01:45, well ahead of it.

## Reference solution
1. List the workspace: README.md and the two oven journals logs/morvane-oven-a.log and logs/morvane-oven-b.log.
2. Read logs/morvane-oven-a.log and note its earliest ERROR stamp: 03:15.
3. Read logs/morvane-oven-b.log: its earliest ERROR is stamped 01:45, earlier than oven A's, so the answer is morvane-oven-b.

## Why the answer is unique
Both files stamp in the same style, so their timestamps compare directly, and the earliest ERROR across the union of the two journals belongs to exactly one oven. A single-file reading produces a plausible wrong answer only by ignoring the second journal entirely. The answer is morvane-oven-b.
