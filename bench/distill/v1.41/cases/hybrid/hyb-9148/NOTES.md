## Traps
- TR-NEARNAME: 北戴河 is a scenic spot / district of 秦皇岛, not a city of its own; get_weather resolves cities only, so asking for 北戴河 returns location not found and the retry is 秦皇岛 (asking for 秦皇岛 straight away is equally good).
- TR-DECOY: 16: tomorrow's low is 16; the day after tomorrow (2026-09-18) is 17.

## Reference solution
1. get_weather {"location": "秦皇岛", "days": 3} (or 北戴河 first, then 秦皇岛 after the not-found error; the same failing name is never retried)
Final answer: 北戴河在秦皇岛，秦皇岛后天（9 月 18 日）多云，最低气温 17°C、最高 29°C，清晨海边有点凉，带件薄外套。

## Why the answer is unique
北戴河 is a seaside district of 秦皇岛; the day after tomorrow is the third forecast row.

## Five alternative phrasings of the task
1. 北戴河后天最低几度
2. 后天早上北戴河冷不冷，最低多少
3. 9 月 18 日北戴河的最低气温
4. 后天去北戴河看日出，要穿多少，先告诉我最低温
5. What will the low be at Beidaihe (北戴河) the day after tomorrow?
