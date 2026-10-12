## Traps
- TR-MULTISRC: 4 per-group tables; the first alone gives 60.
- TR-DECOY: 「上线成功后回滚」 contains 「上线成功」 as a substring; 发布/说明.md says the status is matched exactly, a substring match gives 409.
- TR-DEFN: aggregating every row regardless of status gives 668.

## Reference solution
1. bash: `cat 发布/2026-10/*.csv | awk -F, '$2=="上线成功"' | wc -l`
Final answer: 十月四个服务结果恰好是「上线成功」的发布共 278 次（上线成功后回滚不算）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are aggregated.

## Alternative phrasings
1. 十月四个服务一共成功上线了几次？按 发布/说明.md 的口径。
2. 发布记录目录下四个服务的表，上线成功的记录合计多少条？
3. 统计十月 gateway 等四个服务发布结果为上线成功的次数。
4. 按发布说明，十月全部服务的成功发布次数是多少？
5. 把四张发布表里结果是「上线成功」的行数加起来是多少？
