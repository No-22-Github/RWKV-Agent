## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory or file but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: `sort names.txt | uniq -c`，需要按次数排序时再接 `| sort -rn`。

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.

## Alternative phrasings
1. 怎么统计 names.txt 里每个名字出现的次数？只要命令，别执行。
2. 给我一条命令，数出 names.txt 各个名字的出现次数，我自己跑。
3. names.txt 每行一个名字，想知道谁出现了几次，命令怎么写？不用你运行。
4. 帮我想一条管道，统计 names.txt 中重复名字的次数，先别执行。
5. 我要看 names.txt 里名字的频次，给命令就好，回头自己执行。
