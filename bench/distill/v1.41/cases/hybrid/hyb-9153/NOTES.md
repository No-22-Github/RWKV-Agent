## Traps
- TR-RULEFILE: the rain clause (60%) does not fire; the cold clause (high < 14°C) does: tomorrow's high is 13.
- TR-DECOY: proceeds: tomorrow is only Cloudy with 30% rain, and today's high of 17 would pass; the 13 high cancels it.

## Reference solution
1. read_file club/race-rules.md (list_files first)
2. get_weather {"location": "Auckland", "days": 2}
Final answer: Cancelled: tomorrow's high in Auckland is only 13°C, below the 14°C limit in the club rules, even though the rain chance is just 30%.

## Why the answer is unique
High 13 < 14 triggers the cold clause; the prompt forbids the other verdict word.

## Five alternative phrasings of the task
1. Under the race regulations, is tomorrow's harbour race in Auckland cancelled?
2. Will the club cancel tomorrow's Auckland harbour race?
3. Check the race regulations against Auckland's forecast for tomorrow
4. Is the Auckland harbour race on tomorrow according to the club regulations?
5. 按俱乐部规则，奥克兰明天的港口帆船赛取消吗？
