## Traps
- TR-DECOY: tests/ 下有两份日志，9 月 28 日夜里那轮有 3 个 FAIL，先读到它、或随手数第一份会答 3。

## Reference solution
1. 列出 tests/ 目录，看到 运行记录-0928夜.txt 与 运行记录-0929晨.txt 两份日志。
2. 打开题面要的 9 月 29 日晨检那份（文件头 2026-09-29 06:40）。
3. 数 FAIL 行：test_door_alarm、test_night_window，作答 2。

## Why the answer is unique
0929晨.txt 的 FAIL 开头结果行恰有 2 行；0928夜.txt 的 3 个 FAIL 属于前一天夜里那轮，不是题面要的晨检轮。两份日志各有完整性页脚（各 12 行），可确认没有读串文件。答案唯一。

## 正确答案
2
