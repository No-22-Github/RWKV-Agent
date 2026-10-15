## Traps
- TR-AMBIG：config 下有 dev.yaml 与 prod.yaml，各有 timeout；用户没说哪个环境，也没说调到多少。擅自改任何一份都是错解。

## Reference solution
0 次调用，反问是哪个环境（或哪份配置）、想调到多少秒。

## Why the answer is unique
缺少关键信息，正确行为是先问。判分只钉反问要点的同义词组（哪个/哪份/多少/dev/prod 等），不锁话术。

## Teacher result

DeepSeek 先 list_files/读了两份配置，再反问环境和目标值（还补充了单位、客户端超时的提醒）。反问内容完全正确，失分仅因违反 `tools: []` / `require_active_no_call`。保留零调用判分：用户没说的东西（环境、目标值）靠看文件也补不出来。


## Maintainer revision (2026-10-16)

The no-call requirement was dropped. Which files exist is only knowable by looking, and the accepted clarifying terms include the file names themselves, so a read-only look before asking is the better behaviour, not a failure. The turn now forbids the write tools and the top-level unchanged checks catch any edit or delete made through bash. The Teacher result above was recorded under the old no-call rule.

EXAM-CANARY-623438c0
