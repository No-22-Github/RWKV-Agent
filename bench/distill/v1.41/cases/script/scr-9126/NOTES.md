## Traps
- TR-READONLY: ARCHIVE=/mnt/old/archive stays on the old mount (脚本/README.md); a global `s#/mnt/old#/mnt/new#` would move it too.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find 脚本 -name '*.sh' | xargs sed -i 's#/mnt/old/backup#/mnt/new/backup#g'`
2. bash: `grep -rn /mnt 脚本`
Turn 2:
1. bash: `sed -i 's#/mnt/new/backup#/mnt/cold/backup#' 脚本/夜间.sh 脚本/周度.sh`
2. bash: `grep -rn /mnt 脚本`
Final answers: DONE (turn 1: five scripts write DEST to /mnt/new/backup; turn 2: 夜间.sh and 周度.sh write to /mnt/cold/backup).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. 脚本里备份路径迁到 /mnt/new/backup（归档路径不动），夜间脚本再改到冷存储
2. 把 DEST 的老盘路径换成新盘，之后夜间脚本用 /mnt/cold/backup
3. 备份路径统一搬家，夜间和周度任务之后单独指向冷盘
4. old/backup → new/backup，夜间.sh、周度.sh 再改 cold/backup
5. Move the backup path in all scripts to the new disk, then point the nightly one at cold storage.
