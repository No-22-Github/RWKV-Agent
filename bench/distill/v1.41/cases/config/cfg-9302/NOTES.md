## Traps
- TR-READONLY: 基础设施/测试旧环境 must stay on redis:6.2-alpine (README).
- TR-DECOY: corp/redis-proxy:6.2-alpine also ends in 6.2-alpine; a bare `s/6.2-alpine/7.2-alpine/` would break it.

## Reference solution
1. bash: `find 基础设施 -name compose.yaml | grep -v /测试旧环境/ | xargs sed -i 's#image: redis:6.2-alpine#image: redis:7.2-alpine#'`
2. bash: `grep -rn 'image:' 基础设施` to confirm the target files changed and the protected ones did not.
Final answer: DONE (缓存, 会话, 队列 and 限流 use redis:7.2-alpine; 测试旧环境 and the redis-proxy images are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 把各服务 compose 里的 redis 镜像升级到 7.2-alpine，兼容性测试环境保持 6.2。
2. 基础设施下 redis:6.2-alpine → redis:7.2-alpine，redis-proxy 不属于这次升级。
3. 升级 redis 镜像标签 6.2 到 7.2（四个服务），测试旧环境不要动，改完回复 DONE。
4. 对 基础设施 里的 compose.yaml 批量把 redis 版本换成 7.2-alpine，README 里说的例外照办。
5. Bump the official redis image to 7.2-alpine in every compose.yaml under 基础设施 except the one the README pins, reply DONE.
