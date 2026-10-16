# b21g 出题脚本（v2.1：JSON/JSONL 与多文件聚合，题号 32201–32250）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`emit()`（由 solve 函数得出答案、写 case/verify/NOTES）、沙箱参考命令回放 |
| `a1.py` `a2.py` | JSONL 计数与分组求和 32201–32214 |
| `b1.py` | 单个大 JSON 嵌套统计 32215–32222 |
| `c1.py` `c2.py` | 多文件遍历 32223–32234 |
| `d1.py` | 两份数据对账 32235–32242 |
| `e1.py` | 算完写结果文件 32243–32250 |

```bash
cd bench/distill/tools/b21g && python3 build.py   # 固定种子，重跑逐字节一致；同时在 just-bash 沙箱回放每题参考命令
```
