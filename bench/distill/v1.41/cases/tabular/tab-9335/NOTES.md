## Traps
- TR-DECOY: exact answer 松泰建材; the loose reading (状态前缀匹配，含已付款(部分)) gives 星河科技.
- TR-TRUNC: the file is 96KB and 1327 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$3=="已付款" {s[$2]+=$4} END{for (k in s) print s[k], k}' 销售/订单.txt | sort -rn | head -1` -> 松泰建材
        the same pipeline prints the total (367228) next to the name
Final answer: 已付款金额合计最高的是松泰建材，合计 367228 元。

## Why the answer is unique
客户 and 状态 are whole-value columns; the leader is ahead by at least 500 yuan. The README (销售/说明.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. 订单.txt 里哪个客户的已付款总额最大？
2. 按说明.md，已付款订单的金额按客户汇总，谁最高？
3. 季度订单中，已付款金额加起来最多的客户是谁？
4. 哪家客户的已付款金额排第一（部分付款不算）？
5. 统计状态恰好是已付款的金额，按客户求和后最大的客户名。
