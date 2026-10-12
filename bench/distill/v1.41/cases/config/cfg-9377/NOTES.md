## Traps
- TR-DECOY: deploy/production.env sets DB_POOL_MAX=40; DB_POOL_MIN=2 sits next to the live key.

## Reference solution
1. read_file deploy/staging.env
Final answer: staging 的 DB_POOL_MAX 是 15（production 是 40，不是它）。

## Why the answer is unique
The user names deploy/staging.env; only its live line holds the answer. deploy/production.env has the same key with 40; DB_POOL_MIN is a different key.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. Bash is offered, but a shell call would be wasted effort.

## Five alternative phrasings of the task
1. staging 环境的 DB_POOL_MAX 是多少？看 deploy/staging.env。
2. deploy/staging.env 里连接池最大连接数写的几？
3. 按 deploy/staging.env，数据库连接池最多开多少个连接？
4. 帮我查 deploy/staging.env 的 DB_POOL_MAX。
5. 测试环境（staging）的连接池上限是多少？
