## Traps
- 结论有「压力不足」「过期」两种不合格，都要列。

## Reference solution
1. Read 消防/点检表.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 整改/待更换.md with the 17 lines below (first line is the head the prompt dictates).
   # 待更换灭火器
   - MH-1201 一楼大厅 过期
   - MH-1206 一楼大厅 压力不足
   - MH-1207 二楼走廊 压力不足
   - MH-1208 配电间 压力不足
   - MH-1215 配电间 过期
   - MH-1217 食堂后厨 过期
   - MH-1223 食堂后厨 过期
   - MH-1227 二楼走廊 过期
   - MH-1229 一楼大厅 压力不足
   - MH-1233 配电间 压力不足
   - MH-1238 食堂后厨 压力不足
   - MH-1240 地下仓库 压力不足
   - MH-1243 食堂后厨 过期
   - MH-1245 食堂后厨 压力不足
   - MH-1249 食堂后厨 过期
   共 15 具
3. Read 整改/待更换.md back to confirm.
Final answer, one sentence: 已把汇总写到 整改/待更换.md，共 17 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
