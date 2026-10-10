## Traps
- 「待核」的还没定论，不算超工时。

## Reference solution
1. Read 汽修/维修工单.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 核查/超工时.md with the 11 lines below (first line is the head the prompt dictates).
   # 超工时工单
   - RO6004 沪C·7M830 更换雨刷
   - RO6007 浙B·9D145 四轮定位
   - RO6013 沪A·3K716 换刹车片
   - RO6015 皖A·2H468 空调清洗
   - RO6016 沪A·3K716 更换雨刷
   - RO6022 苏E·58Q02 更换雨刷
   - RO6026 苏E·58Q02 更换机油
   - RO6028 沪C·7M830 更换机油
   - RO6030 苏E·58Q02 更换雨刷
   共 9 单
3. Read 核查/超工时.md back to confirm.
Final answer, one sentence: 已把汇总写到 核查/超工时.md，共 11 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
