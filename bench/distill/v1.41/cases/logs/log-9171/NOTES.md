## Traps
- TR-MULTISRC: four daily logs; the first alone gives 36.
- TR-DECOY: svc=payment-gw, msg=timeout_retry and WARN-level timeouts share the words; a loose `grep payment | grep timeout` gives 309. 日志/说明.md pins full-field matching.

## Reference solution
1. bash: `cat 日志/*.log | grep -c 'level=ERROR svc=payment msg=timeout$'`
Final answer: 这四天 payment 服务的 ERROR 级别 timeout 一共出现 136 次。

## Why the answer is unique
level, svc and msg are all matched as whole fields, and every line ends right after msg.

## Five alternative phrasings of the task
1. 支付服务 payment 的 timeout 错误这几天一共出现了多少次？口径见 日志/说明.md。
2. 四天的日志里，level=ERROR、svc=payment、msg=timeout 的行有多少行？
3. 统计 payment 服务 ERROR 级别的 timeout 次数（网关和重试不算）。
4. 日志 目录下，支付服务报 timeout 错误的总次数是多少？按 说明.md 完整匹配。
5. 9 月 10 到 13 日 payment 的超时错误总共多少条？
