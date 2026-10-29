# b23d 出题脚本（v2.3：3–4 个用户轮，题号 35201–35260）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`mk()`（由声明式 edits/adds/writes 推出最终文件态，写 case/verify/NOTES） |
| `d1a.py` `d1b.py` `d1c.py` | D1（3 轮）35201–35235 |
| `d2a.py` `d2b.py` | D2（4 轮）35236–35260 |

```bash
cd bench/distill/tools/b23d && python3 build.py   # 无随机性，重跑逐字节一致
```
