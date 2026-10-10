## Traps
- TR-MULTISRC: 只在下单日志报错的订单（DD-88714、DD-88667、DD-88274）与只在仓储日志报错的订单（DD-88147、DD-88891、DD-88779）在各自一侧都像答案；DD-88157 在下单侧只有一条「支付风控人工复核中」WARN，配上仓储侧的 ERROR 很容易被当成两边都失败。两边都出现 ERROR 的订单只有 DD-88312。

## Reference solution
1. 读 README.md：两份日志的行格式，一行属于写明的订单号。
2. 检索 logs/qiandan-2026-08-12.log 里的 ERROR 行，收集订单号。
3. 检索 logs/cangku-2026-08-12.log 里的 ERROR 行，收集订单号。
4. 取交集；DD-88157 的下单侧记录是 WARN，级别不符，排除。
5. 交集里唯一的订单号是 DD-88312。

## Why the answer is unique
README 把订单号定为关联键，每行都写明服务，WARN 不算 ERROR，其余订单号都只在一侧失败。交集恰好一个订单号：DD-88312。
