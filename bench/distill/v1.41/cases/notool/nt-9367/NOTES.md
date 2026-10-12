## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or listing/reading the files first, breaks the request.

## Reference solution
No tool call. Final answer: `sort 名单/报名表.txt | uniq -d`。

## Why the answer is unique
The user said not to run anything; any tool call violates the request. The reply must contain the command (one of ['uniq -d', 'uniq -D', 'awk']).

## Five alternative phrasings of the task
1. 用命令把 名单/报名表.txt 里出现不止一次的姓名找出来，每个只显示一次。只写命令，不要跑。
2. 写一条命令，列出 名单/报名表.txt 中重复的名字（去重后显示）。先不要执行。
3. 怎么找 名单/报名表.txt 里重复报名的人？给出命令，我自己执行。
4. 给我一个 sort 加 uniq 的组合命令，输出 名单/报名表.txt 中重复的姓名。不要运行。
5. 报名表里有重复姓名，请写出只显示这些重复姓名的命令，不用运行它。
