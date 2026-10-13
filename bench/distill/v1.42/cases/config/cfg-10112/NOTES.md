## Traps
- TR-READONLY: 停用 stay unchanged per 定时任务/README.md.
- Decoy line `日志时区=UTC` shares text with the target line.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 定时任务 -name 'cron.conf' -not -path '*/停用/*' | xargs sed -i 's|^时区=UTC$|时区=Asia/Shanghai|'`
2. bash: `grep -rn '时区' 定时任务`
Final answer: 已按要求改完，保护目录和相似的行都没动，grep 检查过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
