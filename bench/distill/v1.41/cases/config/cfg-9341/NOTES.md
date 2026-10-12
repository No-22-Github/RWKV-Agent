## Traps
- TR-DECOY: INFO lines carry look-alikes (`ERROR_RATE=0.00`, `errors=0`), only the third field decides the level. TR-READONLY: config/_base/defaults.yaml and connect_timeout_ms stay (config/README.md); a global `s/3000/6000/` or `s/timeout_ms: .*/` hits the wrong lines.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in logs/*.log; do echo "$f $(awk '$3=="ERROR"' $f | wc -l)"; done`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/^timeout_ms: 3000$/timeout_ms: 6000/' config/payment/prod.yaml config/payment/staging.yaml config/payment/canary.yaml`
2. bash: `grep -rn '^timeout_ms' config/payment`
Turn 3 (edit, reply DONE):
1. bash: `sed -i 's/^timeout_ms: 6000$/timeout_ms: 3000/' config/payment/staging.yaml config/payment/canary.yaml`
2. bash: `grep -rn '^timeout_ms' config/payment`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 哪个服务的 ERROR 日志最多？把它的超时翻倍，然后 staging 和 canary 再还原
2. 找出报错最多的服务，三套配置的 timeout_ms 提到 6000，之后只留 prod 的改动
3. 日志里 ERROR 行数最多的是谁？给它的 prod、staging、canary 加长超时，再把后两个撤回
4. 统计各服务 ERROR 行，对出错最多的服务调大 timeout_ms，随后 staging 与 canary 恢复原值
5. Which service logs the most ERROR lines? Raise its timeout_ms to 6000 everywhere, then put staging and canary back to 3000.
