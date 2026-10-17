# b21n 出题脚本（v2.1：代码仓库任务，题号 33501–33570）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`make()`（写 case/verify/NOTES）、沙箱实测 `run_checks()` |
| `gen.py` | 填充代码生成器（py/js/ts/go/sh/yaml） |
| `s1.py` | locate_definition 33501–33512 |
| `s2.py` | find_callers 33513–33524 |
| `s3.py` | count_markers 33525–33536 |
| `s4.py` | fix_edge_case 33537–33548 |
| `s5.py` | explain_readonly 33549–33559 |
| `s6.py` | report_test_result 33560–33570 |

```bash
cd bench/distill/tools/b21n && python3 build.py   # 固定种子，重跑逐字节一致
```
