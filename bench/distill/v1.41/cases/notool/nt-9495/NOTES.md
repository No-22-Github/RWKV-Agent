## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `cp -a /data/reports /data/reports_bak`（或 rsync -a）。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['cp -a', 'cp -p', 'cp -rp', 'cp -pr', 'cp -r', 'rsync', '-a'].

## Five alternative phrasings of the task
1. 给我一条命令：复制 /data/reports 到 /data/reports_bak，时间戳和权限都要保留。不要执行。
2. 怎么把 /data/reports 完整备份成 /data/reports_bak 且保留属性？只写命令。
3. 写命令即可，不要跑：目录 /data/reports 拷贝为 /data/reports_bak，保持原文件时间和权限。
4. 用 cp 复制整个 /data/reports 到 /data/reports_bak 并保留属性，命令怎么写？别运行。
5. 我要给 /data/reports 做个带时间戳的副本 /data/reports_bak，请给命令，不执行。
