## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or listing/reading the files first, breaks the request.

## Reference solution
No tool call. Final answer: `find 项目 -type d -empty`，提醒用户自己执行。

## Why the answer is unique
The user said not to run anything; any tool call violates the request. The reply must contain the command (one of ['-empty']).

## Five alternative phrasings of the task
1. 写一条命令列出 项目 目录下所有空文件夹，只要路径，不要执行。
2. 怎么用命令找出 项目 里的空目录？写出来就行，我自己跑。
3. 给我一条能把 项目 目录中没有任何内容的文件夹列出来的命令，先别运行。
4. 我想清理 项目 里的空目录，先给我列出它们的命令，别帮我执行。
5. 请只告诉我命令：列出 项目 下的空目录。不用运行。
