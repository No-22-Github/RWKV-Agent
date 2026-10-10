## Traps
- TR-DECOY: the sheet has three tickets, but 7号桩 计费板更换 is 未完成 and
  waits for parts; logging all three is the trap.

## Reference solution
1. Read README.md: only tickets marked 完成 that day enter the log, one line `日期 N号桩 事项 完成 工单号`, dated from the sheet header.
2. Read sheets/工单-2026-09-29.txt.
3. Read the tail of logs/repair-2026-09.txt to match the line style.
4. Append the 3号桩 and 5号桩 lines under 2026-09-29.

## Why the answer is unique
7号桩 的工单状态是未完成，README 规定未完成的等修好后再记，提前入日志等于
记录一次没有发生的修复；两条已完成工单的字段照抄工单，日期取表头，行式由
旧行固定，所以追加的块恰好两行。
