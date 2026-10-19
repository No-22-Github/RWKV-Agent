# b22e 出题脚本（v2.2：大文件先看规模，题号 34401–34450）

`python3 build.py` 写 50 题到 `bench/distill/v2.2/cases/{logs,tabular,filesystem}/`，固定种子，重跑逐字节一致；之后在 just-bash 沙箱里真跑每题的参考命令，输出必须含正确答案。

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`make()`（写 case/verify/NOTES，校验 fixture 规模、答案不在第一屏）、`run_checks()` 沙箱实测 |
| `lg.py` | 日志生成：时间线、nginx/syslog/应用/jsonl/中文日志行、植入（plants） |
| `e1a.py` `e1b.py` | E1 大日志 log-34401…34425（8 题需 grep 行号再 read_file 读上下文） |
| `e2a.py` `e2b.py` | E2 大表格 tab-34426…34440 |
| `e3.py` | E3 大目录 fs-34441…34450（300+ 个文件） |

判据：首轮 `required_tools: ["bash"]`（上下文题加 `read_file`）；case 级 `expect.max_calls: {"read_file": 3}`；数字用 `output_contains_any`（含千分位写法）+ token，字符串用 `output_contains`。`verify.py` 先校验 fixture 的 sha256 再由 fixture 重算答案。
