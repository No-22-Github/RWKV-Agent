## Traps
- TR-MULTISRC: 网关日志里只有服务代码（SVC-P2 等），题面给的是服务名称「支付回调服务」，必须先在 服务清单.csv 里把名称对到 SVC-P2 再数。直接数全部 ERROR 行会得到 39（SVC-P2 26 + SVC-A1 7 + SVC-OD 6），只看日志不做名称对码也容易数成别的服务。

## Reference solution
1. 读 服务清单.csv：支付回调服务 → SVC-P2。
2. 数 gateway-20260912.log 里同时含 [ERROR] 与 SVC-P2 的行：14:00 前 10 行、14 点段 8 行、19 点段 8 行。
3. 合计 26。

## Why the answer is unique
题面问的是支付回调服务一家的 ERROR 次数，服务代码与名称的对应关系只有服务清单一份，SVC-P2 的 ERROR 行逐行可数且互不重叠；把别的服务（SVC-A1/SVC-OD）或全部 ERROR 计入的 39 与「支付回调服务」这一定语直接矛盾。答案唯一为 26。
