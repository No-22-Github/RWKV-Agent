## Traps
- TR-DEFN: 周五 is 2026-09-18, the third forecast row (days must be >= 3); only the placeholder line changes and the other lines stay byte-identical.
- TR-DECOY: tomorrow (晴 18~27°C 5%) is the wrong row.
Newline policy: only the placeholder text is replaced; the trailing newline stays.

## Reference solution
1. get_weather {"location": "天津", "days": 3}
2. replace_lines (or write_file) 行程/周五.md line 4 -> "- 天气：多云 19~29°C，降水概率 10%"
3. read_file 行程/周五.md to confirm
Final answer: 已把周五天津的预报（多云 19~29°C，降水概率 10%）填进 行程/周五.md。

## Why the answer is unique
周五 is the third forecast row; the line format is fixed by the prompt.

## Five alternative phrasings of the task
1. 把天津周五的天气填进行程
2. 行程/周五.md 的天气那行补上天津周五预报
3. 周五天津天气写进行程文件
4. 填一下周五行程里的天气
5. Fill the weather line in the Friday plan for Tianjin.
