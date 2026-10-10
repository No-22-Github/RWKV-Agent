# hyb-7733 NOTES

- 会话形状：寒暄后派活（第 1 轮纯寒暄零调用，第 2 轮普通工具题）。
- 语言：英文。第 1 轮判据为零调用 + 应答词表；第 2 轮数值判（答案 18）。

## Traps

- TR-HEADER: deliveries/september_week1.csv 末行是 TOTAL 合计行（branch、item 为空，dozens 为 30，等于全表之和）。不注意会得到：直接把合计行的 30 当作答案，trap_decoys 记 30；或把合计行也加进筛选结果得 48。

## Reference solution

1. 第 1 轮：用户只是寒暄，直接回应问候即可，不调用任何工具（判据要求零调用且回复含应答词）。
2. 第 2 轮：读取 deliveries/september_week1.csv（全程第 1 次工具调用；题面已给路径）。
3. 取 branch 为 Riverside 且 item 为 croissant 的三行，dozens 求和：7 + 6 + 5 = 18（ref_calls = 1）。

## Why the answer is unique

题面问的是 Riverside 分支、croissant 这一个品项的数十。合计行的 30 覆盖全部分支与全部品项（含 sourdough、rye 和 Harbourview 的行），把 30 当答案多算了 sourdough 的 4、rye 的 3 和 Harbourview 的 5 加合计自身，与问句的定语不符；把合计行再加进 Riverside croissant 的筛选得 48，等于把 30 又重复算了一遍，而合计行的 branch 与 item 都是空，不满足任何筛选条件。18 只由三行 Riverside croissant 组成。

## Five alternative phrasings

1. Count the croissant dozens delivered to Riverside in week 1 of September; sheet at deliveries/september_week1.csv.
2. deliveries/september_week1.csv - how many dozens of croissants went to the Riverside branch?
3. Tell me the Riverside croissant total for the first September week, final figure only.
4. How many croissant dozens did Riverside receive that week? Data is in deliveries/september_week1.csv.
5. Give me the Riverside branch croissant dozens from the week 1 delivery sheet.
