# b21c 出题脚本（v2.1，题号 31201–31280）

查不到就说没有，共 80 题。`python3 build.py [--stats]` 重写题目（无随机数，重跑逐字节一致）。

| 文件 | 题号 | 子类 |
| --- | --- | --- |
| `a_key.py` | 31201–31220 | 缺键（其他环境有、近名键） |
| `b_file.py` | 31221–31235 | 缺文件（有相近名字的文件） |
| `c_stale.py` | 31236–31250 | 过期值（作废/被取代/日期已过） |
| `d_conflict.py` | 31251–31265 | 来源冲突（有优先级说明 8 题 / 无法判定 7 题） |
| `e_partial.py` | 31266–31280 | 部分可答 |

`common.py`：词表（absent/stale/conflict）、`claims()` 肯定句生成器、`mk()`（奇数题号不写 tool_policy 且不要求 required_tools，偶数题号 must_offer 只放 read_file[+list_files]）。
