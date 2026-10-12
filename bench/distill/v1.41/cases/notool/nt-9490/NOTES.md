## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: -15 发送 SIGTERM，进程可捕获并清理后退出；-9 发送 SIGKILL，内核强制终止，无法捕获，应作为最后手段。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['SIGKILL', 'SIGTERM', '强制', '优雅', '清理', '无法捕获', '不能被捕获'].

## Five alternative phrasings of the task
1. 杀进程时 kill 和 kill -9 区别在哪？
2. SIGTERM 和 SIGKILL 有什么不同，该先用哪个？
3. 为什么不建议一上来就 kill -9？
4. kill -15 杀不掉的时候再用 -9，原因是什么？
5. 解释一下 kill 的 15 号和 9 号信号。
