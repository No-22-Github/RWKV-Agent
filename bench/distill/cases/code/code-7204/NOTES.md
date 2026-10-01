## Traps
- TR-DECOY: 规范源文件里 push_frame_cmd 的名字先于定义出现——一条 TODO 注释（第 610 行）和一条日志模板字符串（第 1050 行）；把第一次命中或回声当成定义会答错行号。定义是唯一的 `def push_frame_cmd(` 行，即第 1778 行。

## Reference solution
1. 读 README.md：规范源文件是 liyun_control/frame_bus.py，行号以该文件为准。
2. 检索 push_frame_cmd，在命中处附近的行段里逐条核对。
3. 注释与日志模板不是定义；定义是 `def` 行。
4. `def push_frame_cmd(` 在第 1778 行。

## Why the answer is unique
README 钉死了规范源文件；定义只可能是 `def` 行，注释与日志模板被排除。文件里该名字回声 3 处，`def push_frame_cmd(` 只匹配一次。答案是 1778。
