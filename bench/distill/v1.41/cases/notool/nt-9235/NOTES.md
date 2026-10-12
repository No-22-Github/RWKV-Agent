## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or even listing the directory, breaks the request.

## Reference solution
No tool call. Final answer: `du -sh data/*/ | sort -rh | head -5`，不执行。

## Why the answer is unique
The user said not to execute; any tool call violates the request.

## Five alternative phrasings of the task
1. 给我一个命令，列出 data 里最占空间的前五个子目录。别运行，我自己跑。
2. 怎么用 du 找出 data 下体积最大的 5 个子目录？写出命令即可，不要执行。
3. 写个 du 加 sort 的命令，查看 data 目录里最大的五个子目录，先不执行。
4. 我想知道 data 下哪五个子目录最大，请只给出命令，不要替我运行。
5. 帮忙拼一条命令：按大小倒序显示 data 的前 5 个子目录，只写命令。
