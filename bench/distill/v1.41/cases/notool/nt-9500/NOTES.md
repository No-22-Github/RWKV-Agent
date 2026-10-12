## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `curl -L --retry 3 -o /tmp/pkg.tgz https://example.com/files/pkg.tgz`（或 wget -t 3 -O）。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['curl', 'wget'].

## Five alternative phrasings of the task
1. 用 curl 或 wget 下载 https://example.com/files/pkg.tgz 到 /tmp/pkg.tgz，要跟随重定向并重试 3 次，写命令别运行。
2. 给我一条下载命令：保存为 /tmp/pkg.tgz，跟随跳转，最多重试 3 次，先不要执行。
3. 怎么命令行下载 https://example.com/files/pkg.tgz 并自动重试？只写出来。
4. 写一条带重试和跳转跟随的下载命令，文件存成 /tmp/pkg.tgz，不用跑。
5. 请给出 curl -L 加重试参数下载 https://example.com/files/pkg.tgz 的命令，输出到 /tmp/pkg.tgz，不要运行。
