## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory or file but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `sed -i 's/8080/9090/g' 配置/*.conf`，并提醒先用不带 -i 的 sed 预览或先备份。

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.

## Alternative phrasings
1. 我想把 配置 里全部 .conf 的 8080 换成 9090，给我一条 sed 命令，不要运行。
2. 写个 sed 批量替换端口 8080 为 9090 的命令，配置 目录下的 conf 文件，我自己跑。
3. 怎么用 sed 一次性改掉 配置/*.conf 里的端口？只要命令，别执行。
4. 不用帮我执行，只告诉我把 8080 改成 9090 的 sed 命令（作用于配置目录的 .conf）。
5. 配置目录里 conf 文件的端口要从 8080 换成 9090，sed 怎么写？先给命令我再确认。
