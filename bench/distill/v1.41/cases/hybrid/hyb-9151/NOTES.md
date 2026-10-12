## Traps
- TR-RULEFILE: two clauses fire at once (low 8 < 10 adds 50; rain 65% >= 60% halves the 80 base to 40) and the discount does not touch the surcharge; total 40 + 50 = 90.
- TR-DECOY: 80: today's low is 12 and rain 10%, so no clause fires and the fee would be the plain 80; tomorrow is 90.

## Reference solution
1. read_file 营地/收费规定.md (list_files first)
2. get_weather {"location": "承德", "days": 2}
Final answer: 一共 90 元：承德明天最低气温 8°C，低于 10°C 加收取暖垫费 50 元；降水概率 65%，达到 60%，基础费 80 元减半为 40 元；40 + 50 = 90 元。

## Why the answer is unique
Base 80 halved = 40, plus 50 cold surcharge = 90; no other combination gives 90.

## Five alternative phrasings of the task
1. 承德营地明天一顶帐篷多少钱，按规定算
2. 明晚承德营地订一顶帐篷一共多少
3. 按收费规定，承德营地明天帐篷总价是多少
4. 承德营地明天晚上一顶帐篷要付多少，算上天气加减费
5. How much for one tent at the Chengde campsite tomorrow night under the fee rules?
