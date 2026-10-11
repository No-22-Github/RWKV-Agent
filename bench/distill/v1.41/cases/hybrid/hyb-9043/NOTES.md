## Traps
- TR-DEFN: 周六 / 周日 are 2026-09-19 / 09-20 (4th and 5th rows, so days must be >= 4 and >= 5); the second turn switches city AND day, so reusing the first forecast gives the wrong line.
- TR-DECOY: 南京 周日 is 晴 22~31°C 5% and 扬州 周六 is 晴 20~30°C 10%; only 南京 周六 (多云 21~29°C 20%) and 扬州 周日 (雷阵雨 21~27°C 75%) belong in the file.
Newline policy: only the placeholder line text is replaced, so every other line and the trailing newline stay as they are; the expected file is `before` with the two placeholders substituted (ends with one newline).

## Reference solution
Turn 1: get_weather {"location": "南京", "days": 4}; replace line 4 of 出行/周末.md; read_file 出行/周末.md.
Turn 2: get_weather {"location": "扬州", "days": 5}; replace line 7; read_file 出行/周末.md.
Final answer: 已把周日扬州的预报（雷阵雨 21~27°C，降水概率 75%）填进「周日」下面；周六南京是多云，文件里两天都已写好。

## Why the answer is unique
The line format is fixed by the prompt; city/day pairs and the fixed clock determine every value.

## Five alternative phrasings of the task
1. 周六南京的天气填进周末出行文件
2. 把南京周六预报写进出行/周末.md 的周六一栏
3. 周日改去扬州，天气补上
4. 扬州周日天气写到文件里再核对
5. Fill the weekend trip file with the forecasts.
