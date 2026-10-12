## Traps
- TR-RULEFILE: the rain clause (>= 50%) fires for tomorrow's 70%; the cold clause (high < 25°C) does not (high 31); 100 * 0.5 * 3 = 150.
- TR-DECOY: 300: today is dry (20%) and would cost the plain 3 x 100; tomorrow is 150.

## Reference solution
1. read_file 乐园/票价规定.md (list_files first)
2. get_weather {"location": "贵阳", "days": 2}
Final answer: 一共 150 元：贵阳明天有雷阵雨，降水概率 70%，达到 50%，全场 5 折，每人 50 元，3 人 150 元。

## Why the answer is unique
100 x 50% x 3 = 150; the cold clause is not triggered.

## Five alternative phrasings of the task
1. 贵阳水上乐园明天 3 个人门票多少钱，按规定算
2. 明天贵阳乐园三个人的票价一共多少
3. 按票价规定，贵阳明天 3 人门票总价
4. 贵阳水上乐园明天三张票要多少钱
5. How much for 3 tickets to the Guiyang water park tomorrow under the pricing rules?
