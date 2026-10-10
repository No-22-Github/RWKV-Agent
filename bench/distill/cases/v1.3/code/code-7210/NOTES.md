## Traps
- TR-DECOY: send_step_cmd 的名字出现在注释（第 562 行）与日志模板字符串（第 945 行）里；按文本出现次数统计会多算。调用点是真实的调用表达式，包内共 11 处。

## Reference solution
1. 读 README.md：统计范围是 nanxi_robot/，调用点指真实调用表达式。
2. 检索 send_step_cmd，在命中处附近的行段里逐条核对。
3. 排除定义本身、注释与日志模板；transmit_step_cmd 是另一个函数。
4. 实际调用 11 处。

## Why the answer is unique
README 定义了范围与调用点；注释与日志模板不是调用表达式，transmit_step_cmd 名字完全不同。包内 send_step_cmd 的调用表达式恰好 11 处。
