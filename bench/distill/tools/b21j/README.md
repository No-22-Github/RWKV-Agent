# b21j 出题脚本（v2.1：不用工具直接回答，题号 33101–33180）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`T()`（单轮判据，默认 `tools: []`）、`make()`、拒答/假完成词表 |
| `r1.py` `r2.py` | 改写/润色/翻译/缩写 33101–33114（rewrite_text） |
| `c1.py` `c2.py` | 代码解释与小段编写 33115–33128（code_help） |
| `f1.py` `f2.py` | 稳定常识 33129–33141（stable_fact） |
| `u1.py` | 单位换算 33142–33154（unit_convert） |
| `s1.py` | 闲聊 33155–33167（smalltalk） |
| `b1.py` | 超出能力范围 33168–33180（beyond_capability） |

```bash
cd bench/distill/tools/b21j && python3 build.py   # 无随机数，重跑逐字节一致
```
