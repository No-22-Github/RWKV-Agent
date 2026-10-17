# b21l 出题脚本（v2.1 第三波：组合任务，题号 33301–33380）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`mk()`（写 case/verify/NOTES，compute 为唯一真值） |
| `a_webedit.py` | web_then_edit 33301–33316 |
| `b_write.py` | tool_then_write 33317–33332 |
| `c_calc.py` | web_then_calc 33333–33348 |
| `d_comp.py` | compound_request 33349–33364 |
| `e_multi.py` | multi_turn 33365–33380 |

```bash
cd bench/distill/tools/b21l && python3 build.py   # 固定种子，重跑逐字节一致
```
