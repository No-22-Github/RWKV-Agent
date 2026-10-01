## Traps
- TR-NEARNAME: the request says 大壶, which the README maps to 二号机 (一号机
  is the small agency pot); editing 一号机's 30 is the trap.
- TR-DECOY: 先煎分钟 and 二煎分钟 both exist on both machines; raising 二号机's
  二煎分钟 18 or the wrong machine's keys is the second trap.

## Reference solution
1. Read README.md: 大壶 maps to 二号机.
2. Read config/decoction.yaml.
3. Change 二号机's 先煎分钟 from 25 to 35, leaving every other line as it is.

## Why the answer is unique
README 明确「大壶＝二号机」，所以 30 属于一号机，不动；先煎分钟 与
二煎分钟 是两个键，目标键 25 只在二号机出现一次，行式保持不变，改完的
文件只有一种。
