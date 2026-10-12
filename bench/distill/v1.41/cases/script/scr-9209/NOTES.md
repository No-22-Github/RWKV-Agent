## Traps
- TR-READONLY: jobs/purge-legacy.sh must keep pointing at the old directory (jobs/README.md).
- TR-DECOY: /tmp/work-cache/ is a different directory that shares the /tmp/work prefix.

## Reference solution
1. bash: `find jobs -name '*.sh' | grep -v purge-legacy | xargs sed -i 's#/tmp/work/#/var/tmp/work/#g'`
2. bash: `grep -rn '/tmp/work' jobs` to confirm the target files changed and the protected ones did not.
Final answer: DONE (ingest, transform, publish and housekeeping use /var/tmp/work/; purge-legacy.sh and the work-cache paths are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 jobs/*.sh 里的临时目录 /tmp/work/ 换成 /var/tmp/work/，work-cache 和 purge-legacy.sh 不动，检查后回复 DONE。
2. 脚本里的 scratch 路径迁移到 /var/tmp/work/，按 jobs/README.md 排除例外，改完确认并回复 DONE。
3. 批量替换 jobs 里各脚本的 /tmp/work/ 为 /var/tmp/work/，注意不要影响 /tmp/work-cache/，完成后回复 DONE。
4. 请更新作业脚本里的工作目录路径（/tmp/work/ → /var/tmp/work/），清理旧目录的脚本保持原样，检查后回复 DONE。
5. jobs 下的 shell 脚本统一改用 /var/tmp/work/ 作为 scratch 目录，README 里说不改的别改，核对后回复 DONE。
