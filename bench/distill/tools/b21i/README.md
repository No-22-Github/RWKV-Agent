# b21i 出题脚本（v2.1 第三波：网页题，题号 33001–33080）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`fx()` 网页 fixture、`T()` 单轮判据、`mk()` 写题（含 verify/NOTES）、失败/空结果词表、`dates()` 日期写法 |
| `a_summary.py` | 33001–33012 摘要页面要点（摘要不含要点，须 fetch；部分追问第二页） |
| `b_compare.py` | 33013–33024 对比两个来源（官方/较新/权威） |
| `c_lookup.py` | 33025–33035 查具体值 |
| `d_latest.py` | 33036–33046 最新稳定版（含本地 pin 对照） |
| `e_error.py` | 33047–33056 报错含义 |
| `f_deprec.py` | 33057–33066 弃用与替代 |
| `g_fail.py` | 33067–33080 页面打不开 / 搜索为空 |

```bash
cd bench/distill/tools/b21i && python3 build.py   # 无随机数，重跑逐字节一致
```
