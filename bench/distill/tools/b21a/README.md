# b21a 出题脚本（v2.1：改已有文件，题号 31001–31075）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、op 应用（sub/app）、`make()`：由 fixture + op 算出 expect.files 与 verify.py |
| `s1a.py` `s1b.py` | 定点改值 31001–31020 |
| `s2.py` | 追加 vs 覆盖 31021–31032（contains 原文 + 新行） |
| `s3.py` | 多处一致修改 31033–31045 |
| `s4.py` | 遵守排除说明 31046–31057 |
| `s5a.py` `s5b.py` | 改完核对 31058–31075 |

```bash
cd bench/distill/tools/b21a && python3 build.py   # 无随机数，重跑逐字节一致
```
