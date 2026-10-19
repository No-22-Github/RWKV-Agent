# b22b 出题脚本（v2.2：给了网址 → 直接读网页，题号 web-34101–34150）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置（work-v3）、`fx()` 网页 fixture、`T()` 单轮判据、`mk()` 写题（verify/NOTES）、词表（无网页能力的说法、读不到的说法）、`dates()` |
| `b1a.py` `b1b.py` `b1c.py` | B1 给网址直接读，34101–34130 |
| `b2.py` | B2 网址打不开，34131–34140（7 题 fixture 无此网址，3 题 fixture 条目带 error） |
| `b3.py` `b3b.py` | B3 网址 + 本地文件，34141–34150 |

```bash
cd bench/distill/tools/b22b && python3 build.py   # 无随机数，重跑逐字节一致
```
