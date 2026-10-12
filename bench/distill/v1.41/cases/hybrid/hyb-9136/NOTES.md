## Traps
- TR-DEFN: turn 2 is another city and another day (后天 = 09-18, the third row), so a second lookup is needed and the new row goes after the first appended one; the date column is 月-日 only.
- TR-DECOY: 大连 tomorrow is 晴 17~24°C 5%; only the third row (阵雨 16~21°C) belongs in the table.
Newline policy: only the named lines are replaced/appended, so every other line and the single trailing newline stay as they are.

## Reference solution
Turn 1: get_weather for the first city; edit the file; read_file to confirm.
Turn 2: get_weather for the new city/day (a different forecast is needed); edit the file again; read_file to confirm.
Final answer: 已把大连后天（09-18）的预报（阵雨 16~21°C）追加到 出游/天气表.md，青岛明天那一行在上面。

## Why the answer is unique
Row layout and dates are fixed by the prompts; the existing rows stay in place and the file ends with one newline.

## Five alternative phrasings of the task
1. 天气表里先加青岛明天，再加大连后天
2. 往出游天气表追加两行：青岛（明天）和大连（后天）
3. 把青岛、大连的预报依次填成表格行
4. 出游表格追加大连后天的天气一行
5. Append Qingdao's and then Dalian's forecast as table rows.
