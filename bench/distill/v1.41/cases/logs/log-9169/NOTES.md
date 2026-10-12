## Traps
- TR-MULTISRC: three daily files; the first alone gives 81 distinct users.
- TR-DECOY: login_sso failures are not login failures (审计/说明.md); counting every failing login* action gives 237.
- Counting events instead of distinct users gives a much larger number.

## Reference solution
1. bash: `cat 审计/events-*.jsonl | grep '"action":"login","ok":false' | grep -o '"user":"[^"]*"' | sort -u | wc -l`
Final answer: 三天里一共有 179 个不同的用户登录失败过（只算 action 为 login，单点登录不算）。

## Why the answer is unique
Failure is action == login and ok == false; users are de-duplicated across all three files.

## Five alternative phrasings of the task
1. 三天的审计日志里，有多少个不同的用户登录失败过？口径见 审计/说明.md。
2. 统计 9 月 12 到 14 日登录失败（不含单点登录）的用户数，同一个人只算一次。
3. 审计 目录的 jsonl 里，action 是 login 且失败的事件涉及多少个去重用户？
4. 这三天一共多少个账号出现过登录失败？按说明.md 排除 login_sso。
5. 去重后，登录失败过的用户有多少个？
