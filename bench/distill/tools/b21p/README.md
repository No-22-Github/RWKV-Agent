# b21p 出题脚本（v2.1 第三波：文件系统 + 日志，题号 33701–33770）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`make()`（写 case/verify/NOTES）、沙箱实测 `run_checks()` |
| `lg.py` | 日志生成辅助（噪声行、时间渲染） |
| `f1.py` | largest 33701–33706、duplicates 33707–33712 |
| `f3.py` | count_by_type 33713–33718、presence 33719–33723 |
| `f4.py` | scoped_delete 33724–33730、按大小/修改时间/内容找文件 33731–33735 |
| `l1.py` | root_cause 33736–33744 |
| `l2.py` | time_window 33745–33753 |
| `l3.py` | locate_error 33754–33761 |
| `l4.py` | count_events 33762–33770 |

`build.py` 写题后在 just-bash 沙箱里真跑每题的参考命令，输出必须含正确答案。无外部随机数，重跑逐字节一致。

```bash
cd bench/distill/tools/b21p && python3 build.py
```
