## Traps
- TR-DECOY: [admin] 段里有同名的 upstream_timeout_sec = 10、log_level = info。只改一处或改错段（把 admin 改成 20 / warn，或 public 只改一次）都会失败。
- 第 2 轮依赖第 1 轮的结果：“刚才改的那个再翻一倍”是 60 的两倍 120，不是原值 30 的两倍（60）。判分只看最终文件，第 1 轮 expect 为 {}（过渡轮，不单独判分）。

## Reference solution
1. 读 conf/gateway.ini；改 [public] 的 upstream_timeout_sec 为 60（共 2 步，含读）。
2. 第 2 轮：改为 120，log_level 改 warn（1 步）。共 3 步。
终态：[public] 段 upstream_timeout_sec = 120、log_level = warn；[admin] 段原样（timeout 10、log_level info、max_conns 20）。

## Why the answer is unique
“再翻一倍”的对象是刚改成的 60，所以是 120；admin 段题面没点名且要求别的不要动。判分钉住整份文件内容（去掉最终换行，允许有或没有末尾 LF），任何多改少改都不过。

## Teacher result
r1 DeepSeek 第 1 轮改对；第 2 轮把日志级别写到第 6 行（实为空行，log_level 在第 5 行），覆盖了段间空行，[public] 与 [admin] 之间的空行丢失且 log_level 仍是 info。文件内容判分失败，老师真实操作错误（行号错位），保留不改判分。

EXAM-CANARY-77af3190
