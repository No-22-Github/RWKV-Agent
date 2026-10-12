## Traps
- TR-MULTISRC: four daily log files; the first alone gives 20.
- TR-DECOY: paths like /api/items/502, /api/items/5021 and /img/502.png contain 502; `grep -c 502` over the logs gives 271. The README says to match the status column exactly.

## Reference solution
1. bash: `cat 网关日志/*.log | awk '$4==502' | wc -l`
Final answer: 9 月 12 日到 15 日状态码为 502 的请求一共 106 条（只按状态码列匹配，路径里带 502 的不算）。

## Why the answer is unique
The status is column 4 and matched exactly; all four files are summed.

## Five alternative phrasings of the task
1. 网关日志里状态码是 502 的请求一共多少条？按 网关日志/说明.md 的口径。
2. 统计 9 月 12 到 15 日四天的网关日志中 502 响应的条数，路径里出现 502 的别算。
3. 四个日志文件里一共出现了多少次 502 状态码？参考说明.md 的计数规则。
4. 网关日志 目录里，状态码列等于 502 的行总共有多少行？
5. 这四天网关返回 502 的请求总数是多少？说明在 网关日志/说明.md。
