## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `find /srv/demo-site -name '*.sh' -exec chmod +x {} +`。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['chmod'].

## Five alternative phrasings of the task
1. 怎么批量给 /srv/demo-site 里的 .sh 文件加执行权限？只给命令，不要执行。
2. 写条命令：/srv/demo-site 下所有 shell 脚本 chmod +x，先别跑。
3. 递归地让 /srv/demo-site 里的 .sh 都可执行，命令是什么？我自己运行。
4. 给我 find 加 chmod 的组合命令，目标是 /srv/demo-site 的 .sh 文件，不要运行。
5. 我想让 /srv/demo-site 下的脚本全部可执行，请写出命令但不要执行。
