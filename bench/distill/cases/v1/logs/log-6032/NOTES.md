## Traps
None. Pallets are sealed lines and the question counts sealed lines inside the window.

## Reference solution
1. List the workspace: README.md and logs/bottling-line.log.
2. Read logs/bottling-line.log and count pallet-sealed lines stamped from 10:00:00 up to 11:00:00: 10:04, 10:19, 10:33, 10:47, 10:52, 10:58 = 6.

## Why the answer is unique
Each sealed pallet produces exactly one line and start/stop lines are different events, so the window cut has one reading and no line sits on a boundary. The answer is 6.
