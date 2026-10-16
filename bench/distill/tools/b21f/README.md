# b21f 出题脚本（v2.1：日志用 bash 统计准，log-32101–32150）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、四种日志渲染（nginx / JSON 行 / key=value / 应用日志）、verify 里用的解析器源码、`case()` |
| `gen.py` | 事件生成（含子串陷阱：状态码同时出现在耗时、字节数、路径里）、按格式的 bash 片段 |
| `lib.py` | 答案评估器（count / top / slowest / firstbefore / firstafter），build 与每题 verify.py 共用 |
| `mk.py` | 拼装一道题：fixture + specs + 每轮参考命令 |
| `m_count.py` 32101–32112 · `m_window.py` 32113–32122 · `m_top.py` 32123–32132 · `m_cross.py` 32133–32140 · `m_anom.py` 32141–32150 | 五个子类 |

```bash
cd bench/distill/tools/b21f && python3 build.py   # 写题 + 在 just-bash sidecar 里逐轮跑参考命令，输出须含全部期望 token
```
固定种子，重跑逐字节一致。`PARTIAL=1` 只用于调试单个模块。
