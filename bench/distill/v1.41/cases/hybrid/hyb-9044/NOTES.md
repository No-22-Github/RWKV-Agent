## Traps
- TR-DEFN: the log line carries the weekday abbreviation (2026-09-17 is Thu) which the forecast does not state; the unit is a bare C and the range uses a hyphen.
Newline policy: the prompt says the file already ends with a newline and must still end with exactly one newline after the new line (expected = before + line + "\n").

## Reference solution
1. get_weather {"location": "Wuhan", "days": 3}
2. append_file logs/weather-log.txt with "2026-09-17 Thu Wuhan Thundery showers 24-31C\n"
3. read_file logs/weather-log.txt to confirm
Final answer: Appended tomorrow's Wuhan forecast (thundery showers, 24-31C) to logs/weather-log.txt.

## Why the answer is unique
Tomorrow is the second forecast row; the line format is spelled out and the file ends with one newline.

## Five alternative phrasings of the task
1. Log tomorrow's Wuhan weather in the same style.
2. Add one line for tomorrow to logs/weather-log.txt.
3. Append Wuhan's forecast for 2026-09-17 to the weather log.
4. Update the weather log with tomorrow's forecast.
5. 把武汉明天的天气按同样格式记到日志里
