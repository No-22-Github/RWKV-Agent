## Traps
- Turn 1: exact answer 街舞社; the loose reading (状态前缀匹配，含到场(补签)) gives 吉他社.
- Turn 2: exact answer 棋牌社; the loose reading (状态前缀匹配，含缺席(请假)) gives 街舞社.
- TR-MULTISRC: 3 files; the first file alone gives 吉他社.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 社团活动/*.txt | awk -F'\t' '$3=="到场" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1` -> 街舞社
        the same pipeline prints the total (897) next to the name
Turn 2: bash: `cat 社团活动/*.txt | awk -F'\t' '$3=="缺席" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1` -> 棋牌社
        the same pipeline prints the total (349) next to the name
Final answer: 缺席人数合计最多的是棋牌社，共 349 人。

## Why the answer is unique
社团 and 状态 are whole-value columns of the tab-separated tables. The README (社团活动/说明.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. 缺席的人数加起来最多的是哪个社团？
2. 三个月里状态是缺席的人数合计，哪个社团排第一？
3. 按说明.md的口径，缺席人数最多的社团是谁？
4. 把状态为缺席的人数按社团汇总，最高的是哪个社团？
5. 请假缺席不算，缺席人数总和最大的社团是哪个？
