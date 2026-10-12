## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `for f in /home/demo/pics/*.jpeg; do mv "$f" "${f%.jpeg}.jpg"; done`。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['mv', 'rename'].

## Five alternative phrasings of the task
1. 怎么批量把 /home/demo/pics 下的 .jpeg 改名为 .jpg？写出命令，别执行。
2. 写一个循环，把 /home/demo/pics 里 .jpeg 文件的后缀换成 .jpg，先不要跑。
3. 给我批量改扩展名的 shell 命令：/home/demo/pics 的 jpeg 变 jpg，只写不运行。
4. 用 for 循环加 mv 或 rename 把 /home/demo/pics 的 .jpeg 统一成 .jpg，请给命令但别执行。
5. 我想统一图片后缀 .jpeg 到 .jpg，目录是 /home/demo/pics，请写命令，不要运行。
