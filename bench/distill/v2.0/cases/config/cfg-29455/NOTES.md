## Traps
- TR-DEFN: the date to use is the one stored in TRIP_DATE (tomorrow), values are bare, and the TRIP_OWNER line stays.
- TR-DECOY: 阴: today's row is 阴; TRIP_DATE points at 2026-09-17 (多云).

## Reference solution
1. get_weather {"location": "杭州", "days": 2}
2. replace_lines (or write_file) on 配置/trip.env: TRIP_WEATHER=多云, TRIP_LOW=20, TRIP_HIGH=27
3. read_file 配置/trip.env to confirm
Final answer: 已把 trip.env 填好：TRIP_WEATHER=多云，TRIP_LOW=20，TRIP_HIGH=27，其他行没动。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. trip.env 里三个空值按杭州明天的预报填上
2. 配置/trip.env 的天气和最低最高温补上杭州 9 月 17 日数据
3. 给 trip.env 填杭州明天的天气、最低温、最高温
4. trip.env 里 TRIP_DATE 那天的杭州预报填进去，不加引号
5. Fill the empty weather, low and high entries in trip.env with Hangzhou's forecast for TRIP_DATE.
