## Traps
- TR-DEFN: the log line carries the weekday abbreviation (2026-09-17 is Thu), which the forecast does not state; bare C suffix, hyphenated range.
- TR-DECOY: today (Thundery showers 26-32C) is the first row; the line is for tomorrow.
Newline policy: expected = before + line + "\n" (file ends with exactly one trailing newline).

## Reference solution
1. get_weather {"location": "Singapore", "days": 3}
2. append_file logs/sg-weather.txt with "2026-09-17 Thu Singapore Cloudy 26-33C\n"
3. read_file logs/sg-weather.txt to confirm
Final answer: Appended tomorrow's Singapore forecast (cloudy, 26-33C) to logs/sg-weather.txt.

## Why the answer is unique
Tomorrow is the second forecast row; the line format is spelled out.

## Five alternative phrasings of the task
1. Log tomorrow's Singapore weather in the same style.
2. Add a line for 2026-09-17 to logs/sg-weather.txt.
3. Append Singapore's forecast for tomorrow to the log.
4. Update the Singapore weather log with tomorrow.
5. 把新加坡明天的天气按同样格式记到日志里
