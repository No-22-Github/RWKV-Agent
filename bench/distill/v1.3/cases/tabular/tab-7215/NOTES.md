## Traps
- TR-HEADER: 末行是系统生成的 9 月全 Estate 合计（site 为 ALL，README 写明不是一笔交易），不做过滤直接对金额列整列求和会把合计行一起算进去，得 43720.14；正确答案是 Riverside Multi-Storey 在 9 月 17 日的合计 396.36。
- LNG: 当日当场的行集中在导出尾部、超出 read_file 的 64 KB 截断线，整读拿不到。

## Reference solution
1. read_file README.md：末行是系统合计，不是交易。
2. search_text "2026-09-17" 定位当日行段，read_lines 读取（Riverside 的行集中在尾部窗口）。
3. 逐行核对 site 为 Riverside Multi-Storey，合计 amount_gbp。
4. 对照文件末行的系统合计行（site=ALL、日期为整月），确认未混入。
5. 终答只报数字 396.36。

## Why the answer is unique
decoy 43720.14 把非交易的系统合计行当成了收入，与 README 矛盾；不过滤日期与场地则把全 Estate 的 9 月流水当成了单日单场收入。行集合被日期与场地两个精确相等条件唯一确定。答案唯一为 396.36。
