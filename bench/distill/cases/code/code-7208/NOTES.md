## Traps
- TR-NEARNAME: 同一文件还定义了 sync_ledger_cache（第 1092 行），名字以 sync_ledger 开头；按前缀检索会把第一次命中当定义。
- TR-DECOY: 一条 TODO 注释（第 584 行）和一条日志模板（第 1014 行）也写着 sync_ledger。定义是唯一的 `def sync_ledger(` 行，即第 1535 行。

## Reference solution
1. 读 README.md：规范源文件是 hanmo_sync/ledger.py，行号以该文件为准。
2. 检索 sync_ledger，在命中处附近的行段里逐条核对。
3. 近名函数、注释、日志模板都不是定义；定义是 `def` 行且名字完全一致。
4. `def sync_ledger(` 在第 1535 行。

## Why the answer is unique
README 钉死了规范源文件；sync_ledger_cache 是另一个函数，注释与日志模板不是定义。文件里 `def sync_ledger(` 只匹配一次。答案是 1535。
