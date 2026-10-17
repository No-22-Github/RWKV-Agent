# b21m 出题脚本（v2.1 第三波，题号 33401–33460）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、词表、verify 模板（沿用 b21d） |
| `p0.py` | confirm / clarify / undo 三个构造函数 |
| `q1-3.py` | 33401–33420 不可逆操作先确认 |
| `r1-3.py` | 33421–33440 指代不清先追问 |
| `u1-3.py` | 33441–33460 撤销刚才的改动 |

```bash
cd bench/distill/tools/b21m && python3 build.py   # 无随机数，重跑逐字节一致
```
