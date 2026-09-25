## Traps
- None. The journal holds one line per step for the day and the closing line accounts for all of them, so counting the STACK lines is the whole task.

## Reference solution
1. List the workspace: README.md and logs/guillotine.log.
2. Read logs/guillotine.log. Eight lines carry STACK: QP-2261 at 07:15:03, QP-2264 at 07:33:51 and 07:48:22, QP-2269 at 08:19:55, QP-2273 at 08:55:33, 09:11:24 and 09:26:58, and QP-2280 at 09:53:41.

## Why the answer is unique
README.md says STACK records one stack put down on the pallet and the closing line reports 19 step lines, which is what the file holds. Eight of those lines carry STACK, so the guillotine put down eight stacks. Counting the jobs instead of the stacks gives five, and counting every step line gives nineteen; neither answers the question.

## Fixture notes
All stamps are UTC on 18 September 2026. A job keeps its identifier through its steps, and the heights differ so the stack lines cannot be taken for each other.
