## Traps
- TR-DEFN: only the two empty values change, quotes and the spaces around = stay, and the [app]/[log] tables are untouched.
- TR-DECOY: 多云: today's row is 多云; the values are for tomorrow (晴).

## Reference solution
1. get_weather {"location": "大连", "days": 2}
2. replace_lines (or write_file) on 配置/app.toml: condition = "晴" and range = "17~23"
3. read_file 配置/app.toml to confirm
Final answer: 已把 app.toml 的 [forecast] 填成 condition = "晴"、range = "17~23"，其他行没动。

## Why the answer is unique
The forecast row for 2026-09-17 is fixed and the line format and newline rule are spelled out in the prompt.

## Five alternative phrasings of the task
1. app.toml 里 forecast 表的天气和温度范围按大连明天填上
2. 配置/app.toml 的空 condition、range 填大连明天预报
3. 给 toml 里 [forecast] 补上大连明天的天气和范围
4. 大连明天的天气写进 app.toml 的 forecast 表，值加双引号
5. Fill the empty condition and range in the [forecast] table of app.toml with Dalian's forecast for tomorrow.
