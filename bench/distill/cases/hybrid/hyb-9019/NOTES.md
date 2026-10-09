## Traps
- TR-RULEFILE: the go/no-go threshold is in site/rules.md (40%); tomorrow's 60% crosses it while today's 35% would not.

## Reference solution
1. read_file site/rules.md
2. get_weather {"location": "Hangzhou", "days": 3}
Final answer: Hold the pour: tomorrow's Hangzhou forecast is light rain with a 60% chance, above the 40% limit in site/rules.md; Friday (25%) looks workable.

## Why the answer is unique
The rule and the forecast together decide; temperature is not limiting.

## Five alternative phrasings of the task
1. Can we pour in Hangzhou tomorrow under our site rules?
2. Is tomorrow OK for the concrete pour?
3. Check tomorrow's weather against the pour rules.
4. Should the crew pour tomorrow?
5. 杭州明天能浇混凝土吗？按我们的规定
