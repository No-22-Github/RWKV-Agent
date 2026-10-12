## Traps
- TR-READONLY: 术语表.md (definition page) and README.md keep the old word; 「客户」 alone (客户支持, 客户反馈, 客户不得) is a different word that `s/客户/终端/` would break.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `sed -i 's/客户端/终端/g' 手册/安装.md 手册/使用.md 手册/排错.md 手册/法务条款.md`
2. bash: `grep -rn '客户端\|终端' 手册`
Turn 2:
1. bash: `sed -i 's/终端/客户端/g' 手册/法务条款.md 手册/安装.md`
2. bash: `grep -rn '客户端\|终端' 手册`
Final answers: DONE (turn 1: 安装/使用/排错/法务条款 say 终端; turn 2: 法务条款 and 安装 say 客户端 again).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. 手册里客户端全改叫终端，法务条款再恢复原词
2. 统一称呼为终端（术语表除外），之后把法务条款里的改回客户端
3. 客户端→终端 批量替换，法务条款那份还原
4. 手册用语改成终端；合同用语的法务条款保留客户端
5. Rename 客户端 to 终端 across the manual, then put the original word back in the legal terms.
