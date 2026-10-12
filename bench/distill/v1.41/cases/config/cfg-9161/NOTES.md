## Traps
- TR-READONLY: conf/local.ini is a personal override (conf/README.md) and keeps timeout = 90.
- TR-DECOY: connect_timeout and timeout_retries are look-alike keys; a prefix-less `s/timeout/request_timeout/` would rewrite them too.

## Reference solution
1. bash: `find conf -name '*.ini' | grep -v local.ini | xargs sed -i 's/^timeout = /request_timeout = /'`
2. bash: `grep -rn timeout conf` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the five service files now use request_timeout; local.ini, connect_timeout and timeout_retries are untouched).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. 把 conf 里每个服务配置中的 timeout 改名为 request_timeout，别动 README 里点名的文件。
2. conf 下的 ini 文件，timeout 这个键统一重命名成 request_timeout，然后确认一下并回复 DONE。
3. 服务配置里的 timeout 项改叫 request_timeout（只改键名），按 conf/README.md 的说明跳过不该改的，改完说一声 DONE。
4. 请在 conf 目录的 .ini 中把 timeout 键重命名为 request_timeout，注意 connect_timeout 之类的不要碰，完成后回复 DONE。
5. 批量把 conf/*.ini 里的 timeout 键名换成 request_timeout，个人覆盖文件除外，检查后回复 DONE。
