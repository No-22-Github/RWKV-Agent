## Traps
- TR-READONLY: scripts/restore-legacy.sh intentionally keeps the old install path (scripts/README.md).
- TR-DECOY: /opt/old-app-data/ is a different mount that starts with the same text; replacing /opt/old-app would break it.

## Reference solution
1. bash: `find scripts -name '*.sh' | grep -v restore-legacy | xargs sed -i 's#/opt/old-app/#/srv/app/#g'`
2. bash: `grep -rn old-app scripts` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four live scripts use /srv/app/; restore-legacy.sh and every /opt/old-app-data path are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. scripts 里的 .sh 把 /opt/old-app/ 都换成 /srv/app/，数据盘 /opt/old-app-data 和 README 里点名的脚本别动，检查后回复 DONE。
2. 脚本里的旧安装路径 /opt/old-app 改成 /srv/app（scripts 目录下），例外看 README，改完核对并回复 DONE。
3. 请更新 scripts/*.sh 里的安装目录：/opt/old-app/ → /srv/app/，不要影响 old-app-data，完成后检查并回复 DONE。
4. 路径迁移：把 scripts 下各脚本引用的旧目录换成新目录，restore-legacy.sh 保持不变，检查后回复 DONE。
5. 批量改 scripts 里的 shell 脚本，/opt/old-app/ 换成 /srv/app/，README 说不能改的保留，确认后回复 DONE。
