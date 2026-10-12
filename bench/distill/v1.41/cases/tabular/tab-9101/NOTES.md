## Traps
- TR-MULTISRC: 4 per-group tables; the first alone gives 26979.24.
- TR-DECOY: 「到账冲正」 contains 「到账」 as a substring; 充值/说明.md says the status is matched exactly, a substring match gives 181933.64.
- TR-DEFN: aggregating every row regardless of status gives 319721.75.

## Reference solution
1. bash: `cat 充值/2026-09/*.csv | awk -F, '$2=="到账" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: 九月到账的充值金额合计 128976.36 元（只算状态恰好是「到账」，冲正的不计）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are aggregated.

## Alternative phrasings
1. 九月四个大区的充值，真正到账的总共多少钱？口径看 充值/说明.md。
2. 按 充值/说明.md 的规定，把九月四个区的到账充值金额加起来是多少元？
3. 统计一下九月全部大区状态为到账的充值总额（元），说明文件在 充值 目录。
4. 充值目录下四个大区的表，到账的金额合计多少元？只要结果数字。
5. 九月份各区充值表中「到账」状态的流水金额之和是多少？
