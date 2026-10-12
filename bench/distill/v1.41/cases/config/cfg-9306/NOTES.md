## Traps
- TR-READONLY: 轮转/审计 must stay daily (说明.txt, compliance).
- TR-DECOY: 轮转/说明.txt itself talks about rotation; it is a note, not a config.

## Reference solution
1. bash: `ls 轮转/* | grep -v 审计 | grep -v 说明 | xargs sed -i 's/^    daily$/    weekly/'`
2. bash: `grep -rn 'daily\|weekly' 轮转` to confirm the target files changed and the protected ones did not.
Final answer: DONE (nginx, 应用, 任务 and 邮件 rotate weekly; 审计 stays daily and the note is unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 轮转配置里的 daily 全部换成 weekly，审计的保持每天。
2. 把 logrotate 的 daily 改为 weekly（nginx、应用、任务、邮件），合规那份别动。
3. 轮转目录下除审计外，频率统一调成每周，改完回复 DONE。
4. logrotate 文件里 `daily` → `weekly`，审计和说明文件不改，完成后回复 DONE。
5. Change the rotation frequency from daily to weekly in the logrotate configs except the audit one, reply DONE.
