## Traps
- TR-DECOY: 上升速度 appears in both the main hoist block (0.8) and the
  standby hoist block (0.5); editing the standby block or both is the trap.

## Reference solution
1. Read README.md: 提升机 is the main hoist; 备用提升机 is standby-only and its parameters stay as they are.
2. Read config/hoist.json.
3. Change the main hoist's 上升速度 from 0.8 to 1.0, keeping the file's indentation and everything else byte-identical.

## Why the answer is unique
README 说明备用提升机参数历来不动，所以 0.5 与巡检块都不在改动范围内；
0.8 只在主提升机块出现一次，按原有缩进只改这一处，改完的文件只有一种。
