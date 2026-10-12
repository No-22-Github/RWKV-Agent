## Traps
- TR-RULEFILE: the window is two days (明天 and 后天); the user asks about 明天 only, and tomorrow alone (10%) would say go ahead, but 后天 (80%) triggers the rule.
- TR-DECOY: today is 40%, outside the window.

## Reference solution
1. read_file 门店/洗车规则.md
2. get_weather {"location": "合肥", "days": 3}
Final answer: 建议改天：规则看明天和后天两天，合肥明天虽然只有 10%，但后天中雨、降水概率 80%，超过 30%，所以不建议现在洗车或办镀膜。

## Why the answer is unique
The local rule fixes a two-day window and a 30% threshold; the forecast supplies the rest.

## Five alternative phrasings of the task
1. 合肥明天洗车合适吗？按店里规则
2. 明天去洗车会不会白洗
3. 合肥这两天适合洗车还是改天
4. 我想明天洗车加镀膜，行吗
5. Is tomorrow a good day to wash the car in Hefei under the shop's rule?
