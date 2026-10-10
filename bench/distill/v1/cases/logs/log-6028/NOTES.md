## Traps
- TR-DECOY: circuit A starts a cycle at 01:59:07, one minute outside the window, and completes it at 02:33 inside the window. A reader who takes the window loosely by what is running or completing during it counts that cycle too and answers 5; started-in-window is 4.

## Reference solution
1. List the workspace: README.md and logs/cip-journal.log.
2. Read README.md: a cycle's start is its own CIP start line; circuits run independently.
3. Read logs/cip-journal.log and count CIP start lines stamped from 02:00:00 up to 04:00:00: 02:11 (B), 02:47 (A), 03:02 (B), 03:22 (A) = 4.

## Why the answer is unique
The question asks for cycles that started in the window, the start line carries the start stamp, and each start belongs to exactly one cycle, so the count of start lines in the window is the answer. The 01:59:07 start fails the window test even though its completion falls inside it; counting it is the decoy 5. The answer is 4.
