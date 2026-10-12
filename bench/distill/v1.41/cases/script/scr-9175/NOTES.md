## Traps
- perl is not installed (`command not found`, exit 127); the script has to be read and redone with awk.
- TR-DECOY: the slowest request overall is a POST to /api/orders (4889 ms); the script only looks at GET rows.

## Reference solution
1. bash: the tool the user named -> exit 127 (`command not found`).
2. bash: `cat 请求/*.log | awk '$2=="GET" && $4>m {m=$4; p=$3} END{print p}'`
Final answer: 脚本会打印「最慢的 GET 请求: /static/app.js」（perl 不可用，我按脚本逻辑用 awk 复算：只看 GET 行，取耗时最大的一条）。

## Why the answer is unique
The script or query text in the fixture fixes the filter exactly; the fallback reproduces it with awk.

## Five alternative phrasings of the task
1. 执行 perl tools/slowest_get.pl，输出里最慢的 GET 请求路径是什么？
2. 跑一下 tools 里的 slowest_get.pl（perl），把它打印的路径告诉我。
3. 用 perl 运行 tools/slowest_get.pl，最慢的 GET 请求是哪个？
4. 帮我运行那个 perl 脚本，看看最慢的 GET 请求的路径。
5. slowest_get.pl 跑出来的最慢 GET 路径是什么？
