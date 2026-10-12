## Traps
- TR-READONLY: nginx/generated is overwritten by the deploy tool (nginx/README.md).
- TR-DECOY: nginx.conf.default is a package default whose name merely contains .conf.

## Reference solution
1. bash: `for f in $(find nginx -name '*.conf' | grep -v /generated/); do echo '# managed by ops-team' >> "$f"; done`
2. bash: `tail -n 1 nginx/conf.d/*.conf` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four conf.d files end with the managed-by line; generated/auto.conf and nginx.conf.default are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 在 nginx 目录里每个 .conf 的最后一行后面加上「# managed by ops-team」，生成目录和默认文件别动，检查后回复 DONE。
2. 请给 nginx/conf.d 里的站点配置结尾追加托管标记「# managed by ops-team」，遵守 nginx/README.md，完成后回复 DONE。
3. nginx 下的 .conf 文件末尾统一补一行 # managed by ops-team，generated 目录除外，核对后回复 DONE。
4. 批量页脚：把「# managed by ops-team」追加到可以手改的 .conf 文件末尾，改完确认并回复 DONE。
5. 每个 nginx 配置（不含自动生成的）最后加一行 # managed by ops-team，然后检查并回复 DONE。
