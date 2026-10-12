## Traps
- TR-DECOY: max_pool_size and pool_size_min are different keys; svc/_template has pool_size = 4 but is a template (svc/README.md). Staging files may hold their own values; only low services' two files change.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep '^pool_size = ' svc/*/config.toml`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/^pool_size = .*$/pool_size = 10/' svc/auth/config.toml svc/auth/config.staging.toml svc/chat/config.toml svc/chat/config.staging.toml svc/media/config.toml svc/media/config.staging.toml`
2. bash: `grep -rn '^pool_size = ' svc`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 哪些服务的连接池太小（pool_size 低于 10）？把它们的生产和 staging 配置都调到 10
2. 找出 pool_size 不足 10 的服务，两份配置里的 pool_size 都设成 10
3. svc 里 pool_size 小于 10 的有哪几个？统一改为 10（config.toml 与 config.staging.toml）
4. 列出池子小于 10 的服务，然后给它们的两份 toml 都把 pool_size 提到 10
5. Which services have pool_size below 10 in config.toml? Set pool_size to 10 in their config.toml and config.staging.toml.
