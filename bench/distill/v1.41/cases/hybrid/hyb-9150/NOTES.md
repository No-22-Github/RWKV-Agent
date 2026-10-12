## Traps
- TR-NEARNAME: 外滩 is a scenic spot / district of 上海, not a city of its own; get_weather resolves cities only, so asking for 外滩 returns location not found and the retry is 上海 (asking for 上海 straight away is equally good).
- TR-DECOY: 27: tomorrow's high is 27; the day after tomorrow (2026-09-18) is 31.

## Reference solution
1. get_weather {"location": "上海", "days": 3} (or 外滩 first, then 上海 after the not-found error; the same failing name is never retried)
Final answer: 外滩在上海，上海后天（9 月 18 日）多云，最高气温 31°C、最低 23°C，降水概率 20%，晚上看夜景天气不错。

## Why the answer is unique
外滩 is a waterfront district of 上海; the day after tomorrow is the third forecast row.

## Five alternative phrasings of the task
1. 外滩后天最高几度
2. 后天去外滩，热不热，最高多少
3. 9 月 18 日外滩的最高气温
4. 后天晚上外滩看夜景，白天最高温是多少
5. How warm will the Bund (外滩) get the day after tomorrow?
