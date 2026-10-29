# b23e 出题脚本（v2.3：改完核验、改不成如实说，题号 35301–35360）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`make()`（回放 ops 得终态、写 case/verify/NOTES）、E2 的中英文词表与自测 `selftest()` |
| `e1.py` | E1 改完回读 35301–35325（cfg/doc/code/hyb） |
| `e2.py` | E2 改不成要如实说 35326–35345 |
| `e0.py` | E0 对照：简单追加/新建，不必回读 35346–35360 |

```bash
cd bench/distill/tools/b23e && python3 build.py   # 固定内容，无随机数，重跑逐字节一致
```
