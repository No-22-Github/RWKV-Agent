## Traps
- TR-READONLY: 编排/_样例 is the copy-me template and stays as it is; minReplicas: 2 is a look-alike key the README says never changes (a global `s/2/4/` or `s/replicas: 2/replicas: 4/` would also hit minReplicas).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find 编排 -name deploy.yaml | grep -v /_样例/ | xargs sed -i 's/^replicas: 2$/replicas: 4/'`
2. bash: `grep -rn replicas 编排`
Turn 2:
1. bash: `sed -i 's/^replicas: 4$/replicas: 2/' 编排/报表/deploy.yaml && sed -i 's/^replicas: 4$/replicas: 6/' 编排/订单/deploy.yaml`
2. bash: `grep -rn replicas 编排`
Final answers: DONE (turn 1: five services at replicas 4; turn 2: 报表 back to 2, 订单 at 6, the rest still 4).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. 编排里 replicas 全部翻倍到 4，再把报表恢复、订单加到 6
2. 给各服务扩容到 4 个副本，然后报表还原成 2、订单调成 6
3. replicas 2 改 4（模板和保底副本不动），之后报表改回去、订单设成 6
4. 大促扩容 4 副本，报表不扩，订单 6 副本
5. Scale every service to 4 replicas, then put reports back to 2 and orders at 6.
