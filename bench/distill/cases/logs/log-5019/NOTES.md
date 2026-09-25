## Traps
- TR-DECOY: logs/edge.jsonl covers 14 and 15 August 2026 and the same four objects recur on both days, so the hero-a.jpg records of 15 August look exactly like the ones the question asks for. Adding them to the 14 August records gives 296942 instead of 148190.

## Reference solution
1. List the workspace: README.md and logs/edge.jsonl.
2. Read README.md: one record per object served, `bytes` is the body size, and the export covers 14 and 15 August 2026.
3. Read logs/edge.jsonl, or filter it to `path` = /img/hero-a.jpg and `ts` on 14 August, and total `bytes`: the 8 records of that day sum to 148190.

## Why the answer is unique
README.md dates the records to two days and the question names one of them, so the 15 August hero-a.jpg records are outside what was asked for; they are the same object served on another day, which is why they read like the wanted ones. The 8 14 August records carry 148190 bytes between them. The decoy 296942 is that sum with the 8 15 August records of the same object folded in, and totalling the whole file answers a third question. With the day taken literally, the answer is 148190.

## Fixture notes
`bytes` is a bare integer in every record so the field can be totalled directly, and no other field carries a body size. Every `ts` is on one of the two days the README names, and the 14 August hero-a.jpg records are spread through the day rather than grouped.
