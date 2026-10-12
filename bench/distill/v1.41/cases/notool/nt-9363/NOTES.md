## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or listing/reading the files first, breaks the request.

## Reference solution
No tool call. Final answer: `sed -n '10,20p' config/server.ini`，并说明 -n 抑制默认输出。

## Why the answer is unique
The user said not to run anything; any tool call violates the request. The reply must contain the command (one of ['10,20p']).

## Five alternative phrasings of the task
1. 用 sed 怎么只打印 config/server.ini 的第 10 到第 20 行？只给命令，不要执行。
2. 写一条 sed 命令，输出 config/server.ini 第 10-20 行，我自己跑。
3. config/server.ini 我只关心 10 到 20 行，给我 sed 命令，先别运行。
4. 请给出用 sed 截取 config/server.ini 第 10 行到第 20 行的命令，不用执行。
5. sed 怎么截取文件的第 10 至 20 行？以 config/server.ini 为例，写出命令就行。
