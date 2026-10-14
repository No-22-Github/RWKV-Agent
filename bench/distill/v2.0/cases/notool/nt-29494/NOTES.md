## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: 2>&1 把标准错误（文件描述符 2）重定向到标准输出（1）当前指向的位置；先 > 文件再 2>&1，两者才都进文件。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['标准错误', 'stderr', '标准输出', 'stdout', '文件描述符'].

## Five alternative phrasings of the task
1. 2>&1 到底是什么意思？
2. 为什么日志重定向要写成 > file 2>&1？
3. 标准错误和标准输出怎么合并到一个文件？
4. 解释 shell 里的 2>&1，顺序为什么重要？
5. 把 stderr 也写进文件的写法是什么，原理是什么？
