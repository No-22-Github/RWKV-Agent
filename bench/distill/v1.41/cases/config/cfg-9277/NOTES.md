## Traps
- TR-READONLY: 部署/_样例.yaml stays. TR-DECOY: `# mirror: registry.old.com` comment lines must keep the old host in every turn (a global `s/registry.old.com/registry.new.com/` changes them).
- Turn 3 undoes both earlier turns: all five manifests end byte-identical to the fixture.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere; turn 3 undoes the whole change.

## Reference solution
Turn 1:
1. bash: `find 部署 -name '*.yaml' | grep -v _样例 | xargs sed -i 's#^image: registry\.old\.com/#image: registry.new.com/#'`
2. bash: `grep -rn 'registry' 部署`
Final answer: DONE (五个服务 image 指向 registry.new.com).
Turn 2:
1. bash: `sed -i 's#^image: registry\.new\.com/#image: registry.old.com/#' 部署/支付.yaml 部署/对账.yaml && sed -i 's#^image: registry\.new\.com/#image: registry.eu.com/#' 部署/搜索.yaml`
2. bash: `grep -rn 'registry' 部署`
Final answer: DONE (支付、对账回旧仓库，搜索用 eu，订单通知用新仓库).
Turn 3:
1. bash: `find 部署 -name '*.yaml' | grep -v _样例 | xargs sed -i -e 's#^image: registry\.new\.com/#image: registry.old.com/#' -e 's#^image: registry\.eu\.com/#image: registry.old.com/#'`
2. bash: `grep -rn 'registry' 部署`
Final answer: DONE (五个服务 image 都回到 registry.old.com).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 仓库迁到 registry.new.com，支付对账回退、搜索改欧洲节点，最后整个迁移取消
2. image 行换仓库（模板与 mirror 注释除外），局部调整后全部还原成 registry.old.com
3. 先迁移镜像仓库，再让两个服务回旧仓库、一个用 eu，最后统一退回最初状态
4. registry.old.com→registry.new.com，随后支付、对账还原，搜索 eu，最后全部恢复
5. Migrate the image registry, keep two services on the old one and one on eu, then cancel everything and restore the original registry.
