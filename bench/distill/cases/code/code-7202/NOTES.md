## Traps
- TR-DECOY: 在包内直接搜 issue_valve_cmd 会命中 24 行名字。其中只有 15 行是真实调用（Call 表达式）；其余是定义本身、valve_ops.py 里的超时与队列异常消息字符串各一行、一条批量模式注释、__all__ 导出表，以及 schedule.py 里的废弃桩 issue_valve_cmd_retry（定义、桩内下线说明字符串、3 处桩调用——函数体只抛 NotImplementedError，从不真实下发）和一条日志模板。按名字行数统计会得到 24；真实调用点是 15。

## Reference solution
1. 读 README.md：调用点统计范围是 heyuan_control/ 目录内全部 Python 文件，注释、字符串、废弃桩不算调用。
2. 在 heyuan_control/valve_ops.py 与 heyuan_control/schedule.py 中搜 issue_valve_cmd（带开括号），逐处用行窗口确认是 Call 表达式。
3. 排除定义本身（valve_ops.py 的 def 一处）与 __all__ 导出表。
4. 排除注释、异常消息字符串、日志模板，以及近名的 issue_valve_cmd_retry（schedule.py 定义 1 处、调用 3 处，且函数体已废弃）。
5. 剩下 15 处真实调用。

## Why the answer is unique
"实际被调用"有客观口径：Call 表达式且函数名为 issue_valve_cmd，定义本身不是调用。注释与字符串里的名字不构成调用，README 也在统计规则里写明；废弃桩 issue_valve_cmd_retry 是另一个函数（搜 issue_valve_cmd( 不会命中它，因为名字后跟的是 _r），其函数体只抛 NotImplementedError。按开括号数文本与按 ast 数 Call 节点两种算法得到同一个数：15。
