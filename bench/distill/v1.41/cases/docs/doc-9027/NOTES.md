## Traps
- TR-READONLY: inside 入门.md and 部署.md the block between 历史:开始 and 历史:结束 is an archive and keeps 星桥 1.8; 更新记录.md is history and keeps every line (文档/README.md).

## Reference solution
1. bash: `find 文档 -name '*.md' | grep -v 更新记录 | xargs sed -i '/历史:开始/,/历史:结束/!s/星桥 1\.8/星桥 2.0/g'`
2. bash: `grep -rn '星桥 [12]' 文档` to confirm 星桥 2.0 outside the archive blocks and 星桥 1.8 only inside them and in 更新记录.md.
Final answer: DONE; 入门、部署、排障 三个文档里存档块之外的「星桥 1.8」都改成了「星桥 2.0」，存档块和更新记录没动。

## Why the answer is unique
The replacement is mechanical outside the two protected ranges; the excluded ranges are byte-identical.
