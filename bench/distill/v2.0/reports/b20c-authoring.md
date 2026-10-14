# b20c 出题报告（v2.0，20081–20140）

## 题数与分布
共 60 题。中文 36（60%），英文 24。多轮 12（20%）。

| 子类 | 题号 | 题数 | never_offer | 多轮 |
| --- | --- | --- | --- | --- |
| A 无 web 问时效 | 20081–20090 | 10（有旧记录 5，无记录 3，多轮 2） | web_search, web_fetch | 2 |
| B 无 get_weather | 20091–20098 | 8（有记录 3，无记录 3，多轮 2） | get_weather +web（6）；仅 get_weather（2） | 2 |
| C 无 bash 做统计 | 20099–20110 | 12 | bash | 2 |
| D 无 data_query | 20111–20120 | 10（bash 5，read_file+calculator 5） | data_query | 2 |
| E 无 list_files | 20121–20128 | 8（bash find 4，search_text 4） | list_files | 2 |
| F 无 calculator | 20129–20134 | 6（awk 2，直接算 4） | calculator | 1 |
| G 无写文件工具 | 20135–20140 | 6（bash sed 4，无 bash 说明 2） | write_file, replace_lines, append_file（+bash 2 题） | 1 |

tool_policy 全部有 never_offer 和 must_offer，不冲突，required_tools 都在 must_offer 内（mk 里断言）。判据只用已有字段。题面不点工具名，不加没必要的 max_output_chars；答案形式写在题面（“只回答数字”“保留两位小数”“只回答文件名”）。

## 自检
- build.py 两次运行逐字节一致（全部 cases 目录哈希比对相同）。
- gate.sh 按 20081–20140 分段跑：lint 0 违规，verify 60/60（glob 20 题那段多混入 1 个别批次题，也通过）。
- `rwkv-lab-v20 corpus loadcheck`：940 题全部加载成功。
- bash 参考解 15 条（C 无；D 5、E 4、F 2、G 4）在 just-bash sidecar 里全部跑通，无 UNVERIFIED。其余 45 题没有 bash 参考解（本来就不走 bash）。

## 已知风险
- 拒答题用词表判“如实说做不了”，词表是穷举的，仍可能漏收老师的某种说法。
- 旧记录题（A/B）用记录里的值（如 5.1.4、33）做 output_contains，不检查日期；“注明日期”靠 NOTES 人审。
- 数字题已全部改为 token 判据（"142" 不再误过 "42"）；代价是中文答成紧贴单位的 "42个" 会漏判，题面都写了“只回答数字”。小数题（平均数/金额/F 组）改用 output_contains_any 收 63.50 / 63.5 / 千分位等写法。A/B 组旧记录里的值（如 33、7.1342）仍是子串匹配。
- B5/B8 只拿掉 get_weather，web 工具可能在场（fixture 为空，应搜不到）；老师可能在搜索失败后给出泛泛的“通常 9 月…°C”，会被 output_excludes 判错。
- F 题 awk 浮点与 Decimal 半入舍入在 .xx5 边界可能不一致，已用参考解验证当前 2 题一致。

## 我认为老师最可能答错的 3 道题
1. web-20086 / web-20090（多轮）：第一轮读到固定版本后，第二轮老师容易把 package.json 里的版本当“最新版本”，或者用训练记忆报一个版本号。
2. hyb-20095（天气，仅拿掉 get_weather）：web_search 在场但无结果时，老师倾向给出“北京九月通常 20–28°C”之类的泛化数字，触发 °C 排除。
3. cfg-20135（bash 改 ini）：[server] 与 [client] 的 timeout=30 重复，且有 connect_timeout=30；老师若全局 sed 会改错，expect.files 整文件相等会判错。（次选 tab-20129 之类 awk 小数题的输出格式。）
