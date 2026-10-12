## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: && 只有前一条命令成功（退出码 0）才执行后一条；; 不论成败都继续执行。

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['成功', '退出码', '前一个', '失败', '返回值', '状态'].

## Five alternative phrasings of the task
1. shell 里 a && b 和 a ; b 有什么不同？
2. && 什么时候不会执行后面的命令？
3. 分号和双与号连接命令的区别是什么？
4. 为什么脚本里常用 && 把几条命令串起来？
5. 解释命令连接符 && 与 ; 的差异。
