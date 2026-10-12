## Traps
- TR-READONLY: 日志轮转/_停用 stays. TR-DECOY: `maxage 7` also contains 7 (an unanchored `s/7/14/` changes it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find 日志轮转 -name '*.conf' | grep -v /_停用/ | xargs sed -i 's/^rotate 7$/rotate 14/'`
2. bash: `grep -rn '^rotate' 日志轮转`
Final answer: DONE (五个服务 rotate 为 14).
Turn 2:
1. bash: `sed -i 's/^rotate 14$/rotate 30/' 日志轮转/支付.conf 日志轮转/认证.conf`
2. bash: `grep -rn '^rotate' 日志轮转`
Final answer: DONE (支付、认证为 30，其余 14).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 日志轮转份数从 7 提高到 14（maxage 和停用任务不动），支付和认证再提高到 30
2. 把 rotate 7 批量改成 rotate 14，之后支付、认证改成 30
3. 各服务日志多保留一倍的份数，其中支付与认证保留 30 份
4. rotate 7→14，支付认证两个再调到 30
5. Raise rotate from 7 to 14 in all active configs, then give payments and auth 30.
