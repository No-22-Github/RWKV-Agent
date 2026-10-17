# b21k 出题脚本（v2.1 第三波：工作区文档类，题号 33201–33275）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置与 `mk()`（写 case/verify/NOTES；verify 从 fixture 重算/校验） |
| `s1a.py` `s1b.py` | draft_document 33201–33219 |
| `s2a.py` `s2b.py` | extract_items / write_structured 33220–33238 |
| `s3a.py` `s3b.py` | policy_lookup 33239–33257 |
| `s4a.py` `s4b.py` | link_check 33258–33275 |

```bash
cd bench/distill/tools/b21k && python3 build.py   # 固定内容，重跑逐字节一致
```
