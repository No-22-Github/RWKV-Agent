## Traps
- TR-DECOY: docs/plan.txt 的「已上线」一行列着等级折扣，粗读容易把它当成待办；同一行还有 PDF 导出。 A careless pass reports `等级折扣`.

## Reference solution
1. Read README.md to see what the project is.
2. Read docs/plan.txt for milestones, shipped work and parked items.
3. Summarize the project and everything still open, shelved items included.

## Why the answer is unique
等级折扣 sits on the 已上线 line, which the plan marks as shipped, so it cannot be outstanding. The plan's own labels split the remaining lines into the M3 milestone, the shelved 多币种报价, the split-service item waiting on ops, and tech debt, and no other line is unfinished, so the open set is exactly those.
