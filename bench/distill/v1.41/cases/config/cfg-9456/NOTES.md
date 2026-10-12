## Traps
- TR-DEFN: the block date (09-18) selects the third row, rain_chance loses its % sign, indentation is kept.
- TR-DECOY: 晴: today's row is 晴; the date in the file is 2026-09-18, the third row (多云).

## Reference solution
1. get_weather {"location": "青岛", "days": 3}
2. replace_lines (or write_file) on 站点/status.yaml for the four fields
3. read_file 站点/status.yaml to confirm
Final answer: 已把 status.yaml 的 forecast 块改成：多云，最低 18，最高 24，降水概率 40，其他行没动。

## Why the answer is unique
The forecast row for 2026-09-18 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. status.yaml 的 forecast 四项按青岛后天预报填
2. 站点/status.yaml 里 date 那天的青岛天气写进去
3. 给 status.yaml 的预报块填青岛 9 月 18 日数据
4. yaml 里天气、最低、最高、降水概率四项改成青岛后天的值
5. Update the forecast block of status.yaml with Qingdao's forecast for the listed date.
