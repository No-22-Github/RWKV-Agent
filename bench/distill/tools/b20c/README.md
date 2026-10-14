# b20c 出题脚本（v2.0，题号 20081–20140）

目录被拿掉一个顺手工具之后的替代与降级，共 60 题。每题用 `tool_policy.never_offer` 固定拿掉工具，`must_offer` 保证替代工具在场。

| 文件 | 题号 | 内容 |
| --- | --- | --- |
| `a_web.py` | 20081–20090 | 没有 web：问时效信息（版本、汇率、现价），部分工作区有带日期的旧记录 |
| `b_weather.py` | 20091–20098 | 没有 get_weather：问天气；有的同时拿掉 web，有的只拿掉 get_weather |
| `c_nobash.py` | 20099–20110 | 没有 bash：用 data_query / search_text / list_files / read_file 做统计 |
| `d_nodq.py` | 20111–20120 | 没有 data_query：5 题用 bash（awk），5 题 read_file + calculator |
| `e_nolist.py` | 20121–20128 | 没有 list_files：用 search_text 或 bash find 找文件 |
| `f_nocalc.py` | 20129–20134 | 没有 calculator：直接算或 awk |
| `g_nowrite.py` | 20135–20140 | 没有写文件工具：用 bash sed 改；或无 bash 时如实说明并给出新内容 |

```bash
cd bench/distill/tools/b20c && python3 build.py      # 写题，并在 just-bash sidecar 里回放 15 条 bash 参考解
python3 build.py --no-sidecar                        # 没有 sidecar 时参考解标 UNVERIFIED
```

- 随机数全部固定种子，重跑逐字节一致。
- `common.cant_words()` 是「无法联网/无法核实/cannot/can't…」词表（中英、大小写、弯引号）。
- 无答案值的拒答题（forbidden_tools + output_contains_any）按 verify 规则走 `verify_skipped_refusal`；其余题 verify.py 先校验 fixture 哈希再重算答案。
- forbidden_tools 在拒答题里放的是 never_offer 的工具：模型若硬调一个目录里没有的工具，会被判出。
- 解题者不得读这里的文件。
