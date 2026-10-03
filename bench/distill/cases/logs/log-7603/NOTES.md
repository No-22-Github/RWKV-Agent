## Traps
- TR-DECOY: logs/card-audit-sep.log mixes two TRAINING opens (card T-0090 on the closed floor-4 rooms) in with guest traffic. Counting every unlock line gives 9 unlocks; README says T-cards are staff training drills on the renovation floor, so genuine guest unlocks are 7.

## Reference solution
1. Read README.md: T-cards are the trainer set, floor 4 is closed for renovation, guest activity is K-cards.
2. Read logs/card-audit-sep.log.
3. Count card K- lines: 7 guest unlocks; room 201 leads with 4; the training entries name card T-0090.

## Why the answer is unique
The decoy 9 unlocks folds the two T-0090 training drills into guest traffic. README assigns every T-card open to the trainer set on the closed renovation floor, so those two lines cannot be guest activity under the file's own rule; the guest count is exactly the K-card lines, 7. Room counts among K-card opens are 201:4, 305:2, 210:1, so the busiest room is 201, and the only entries needing explanation are the two TRAINING lines naming card T-0090. No other reading of the log produces a different guest count or busiest room.

## Changelog
- 2026-10-04 verify.py：c1e2d99 起 bank verify 把 output_contains 里的数字也拿来做破坏测试（+1），命中的是与答案无关的字面量（时间戳 / 装备数量），原 verify.py 察觉不到。补了对应位置的格式或内容校验；题目、判据、fixture 均未改，旧路径照常有效。
