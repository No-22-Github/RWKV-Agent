## Traps
- TR-DATEFMT: 东片区的登记员把交易日期写成 DD/MM/YYYY（README 写明，其余片区是 YYYY-MM-DD）。只按 2026-09-12 过滤会漏掉东片区当天的 9 张票，得 26 家；把 12/09/2026 的票也算进来，当天不同的摊位共 34 家。
- LNG: 东片区当天的票集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：东片区用 DD/MM/YYYY，其余片区用 YYYY-MM-DD。
2. search_text "2026-09-12" 定位 ISO 行段并 read_lines，去重计摊位。
3. search_text "12/09/2026" 定位东片区行段（尾部）并 read_lines，去重计摊位。
4. 两种写法的票互不重叠，合并后共 34 家；终答只报数字 34。

## Why the answer is unique
decoy 26 等于宣布东片区当天没人出摊，与 README 写明的登记格式矛盾；两种写法的票互不重叠，12 日之外的日子被日期条件排除。答案唯一为 34。
