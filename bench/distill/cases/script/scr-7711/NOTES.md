## Traps
- TR-DECOY: the run record holds two tracebacks - yesterday's TypeError on the totals line, marked as fixed the next morning, and today's ValueError on 缺卡. Chasing yesterday's already-repaired line leaves tonight's crash in place.

## Reference solution
1. 读 logs/盘点夜批-2026-09-28.log：上半段是 09-27 已修复的 TypeError，当下这次中断是 09-28 深夜的 ValueError，int('缺卡')。
2. 读 stock.py：盒数一格直接进 int()。
3. 读 stock/2026-09.csv：09-19 经络贴剂一格是「缺卡」。
4. 读 README.md，把 stock.py 修成「缺卡」按零计入，与说明文字一致。

## Why the answer is unique
把「缺卡」按零计入后，合并两份盘点（跑分时会再放入 stock/2026-10.csv，其中家用器械同样缺卡）正好是 家用器械,39 / 感冒类,58 / 经络贴剂,0 / 营养保健,47 / 合计,144。说明文字与 README 都写明缺卡按零计入；昨天那条 TypeError 已在日志里标注修复完毕，且当前脚本里根本没有它指向的拼接写法，沿它修没有任何可改的东西。
