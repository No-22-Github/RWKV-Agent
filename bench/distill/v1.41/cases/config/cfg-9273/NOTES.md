## Traps
- TR-READONLY: 微服务/_样例 keeps retries: 1. TR-DECOY: 物流 (retries: 2) and 风控 (retries: 5) already differed before turn 1 and are not 1, so the edit leaves them; the turn-2 list is those two plus the template.
- Turn 2 asks about the whole tree, including files that already differed before turn 1.

## Reference solution
Turn 1:
1. bash: `find 微服务 -name conf.yaml | grep -v /_样例/ | xargs sed -i 's/^retries: 1$/retries: 3/'`
2. bash: `grep -rn '^retries' 微服务`
Final answer: DONE (五个服务 retries 为 3).
Turn 2:
1. bash: `grep -rL '^retries: 3$' 微服务 --include=conf.yaml`
Final answer: 物流、风控、_样例.

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 改完之后，哪几个服务的重试次数不是 3？
2. 列出现在 retries 不等于 3 的服务目录
3. 还有哪些 conf.yaml 没有 retries: 3？只要目录名
4. retries 不是 3 的服务有哪些（含模板目录）？
5. Which service directories do not have retries 3 now?
