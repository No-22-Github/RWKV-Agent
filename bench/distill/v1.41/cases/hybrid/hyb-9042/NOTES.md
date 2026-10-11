## Traps
- TR-NEARNAME: 洱海 is a lake near 大理, not a city; get_weather resolves cities only, so asking for 洱海 returns location not found and the retry is 大理.
- TR-DECOY: tomorrow's high is 25; 后天 (2026-09-18) is 27.

## Reference solution
1. get_weather {"location": "大理", "days": 3} (or 洱海 first, then 大理 after the not-found error)
Final answer: 后天（9 月 18 日）大理晴，最高气温 27°C、最低 15°C，适合骑行；洱海在大理，按大理的预报看。

## Why the answer is unique
后天 is the third forecast row; the lake has no separate forecast.

## Five alternative phrasings of the task
1. 后天洱海边最高多少度？
2. 后天去洱海骑车，热不热？
3. 大理后天最高气温是多少？
4. 9 月 18 日洱海气温
5. How hot will it be at Erhai Lake the day after tomorrow?
