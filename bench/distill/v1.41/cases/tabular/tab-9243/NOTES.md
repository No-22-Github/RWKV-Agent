## Traps
- Turn 1: exact answer 16320; the loose match (仪器包含显微镜，含显微镜-备用) gives 24240.
- Turn 2: exact answer 183; the loose match (预约人包含陈琳，含陈琳琳) gives 252.
- TR-MULTISRC: 3 files; the first file alone gives 51.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `cat 实验室/*.txt | awk -F'\t' '$2=="显微镜" {s+=$4} END{print s}'` -> 16320
Turn 2: bash: `cat 实验室/*.txt | awk -F'\t' '$3=="陈琳"' | wc -l` -> 183
Final answer: 陈琳共预约 183 次。

## Why the answer is unique
仪器 and 预约人 are exact columns. The README (实验室/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 三个月的记录里，预约人是陈琳的有多少条？
2. 陈琳一共约了几次仪器？
3. 统计预约人为陈琳的记录条数（不分仪器）。
4. 按说明.md，陈琳（不是陈琳琳）总共预约多少次？
5. 三份预约表里陈琳出现了多少次？
