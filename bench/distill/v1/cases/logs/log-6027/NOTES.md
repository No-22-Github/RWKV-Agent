## Traps
None. Loads are load lines and the question counts load lines inside the window.

## Reference solution
1. List the workspace: README.md and logs/oven-log.log.
2. Read logs/oven-log.log and count load lines stamped from 06:00:00 up to 08:00:00: 06:05, 06:50, 07:15, 07:58 = 4.

## Why the answer is unique
load and unload are distinct event kinds on one line each, and no line sits exactly on a window boundary, so the count has one reading. The 03:30 and 09:10 loads fall outside the window. The answer is 4.
