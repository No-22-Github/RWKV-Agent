# b21g 出题报告（v2.1，32201–32250，JSON/JSONL 与多文件聚合）

## 数量与分布
- 共 50 题：JSONL 计数/分组求和 14（32201–32214）、单个大 JSON 嵌套统计 8（32215–32222）、多文件遍历 12（32223–32234，目录 90–150 个文件，list_files 一次列不全）、两份数据对账 8（32235–32242）、算完写结果文件 8（32243–32250，`expect.files` equals）。
- 场景前缀：tab 30（JSONL 14、嵌套 JSON 5、对账 8、写文件 3）、fs 10（多文件 8、写文件 2）、cfg 10（嵌套 JSON 配置 3、多文件 4、写文件 3）。
- 中文 26 / 英文 24（52%）；多轮（≥2 个用户轮）23（46%）；难度 L1 18 / L2 20 / L3 12，无 L0。
- tool_policy：全部 must_offer bash + 一个读工具（read_file / list_files / search_text 按题号轮换），never_offer web_search、web_fetch；其中 17 题（34%，题号能被 3 整除）另 never_offer calculator 和 data_query，其余不限。
- 首轮 `required_tools: ["bash"]`（数据量/文件数让不用 bash 基本做不下来）。

## 判据设计
- 全部用 `output_contains`（整词匹配）：主数字 + 对账/排名题终答里列出的条目（发票号、设备名、文件名等）逐个判；金额带两位小数的题用 `output_contains_any` + `output_contains_any_token` 收 `48215.30 / 48,215.30 / 48215.3 / 48,215.3` 四种写法（jq 会吞掉末尾 0）。
- 写文件题：`expect.files` 对结果文件 `equals`（含末尾换行，格式在题面里逐字说清），其余 fixture 文件 `unchanged`；多轮写文件题第二轮才要求落盘。
- 每题 `trap_decoys` 给出"走捷径"的错误值（前缀/子串匹配、忽略 null、只看一个目录、不递归、全量而非过滤等），已断言与正确答案不同。
- 不设 `max_output_chars`；题面不点工具名，不出现 jq。
- verify.py：先校验 fixture sha256，再用同一份 `solve()`（纯标准库 Python）从 fixture 重算；builder 里用的是同一函数源码，所以出题与验证不会漂移。

## 参考命令已在沙箱跑通
- build.py 对每题最后一轮的参考 bash 命令（jq / grep / awk / find / comm / sort / uniq）在 just-bash 沙箱真跑，并核对 stdout 含与 solve 一致的数字与条目；写文件题用沙箱 `read` 读回覆盖层，核对文件内容与 `expect.files` 逐字相同。50/50 通过。
- jq 实测：可用且功能较全——`-s -r -c -n --arg --slurpfile`、`group_by unique_by sort_by min_by max_by`、`// 默认值`、`?`、`test sub split join ltrimstr tonumber`、`@csv @tsv`、`recurse ..`、`index has keys`、`limit`、`reduce`。不支持或有坑：`--version`、`inputs`、`input_filename`、`@sh` 带插值、`walk` 结果不对、`-e` 不改退出码；浮点求和会出 0.30000000000000004，金额要 `*100|round/100`。yq 可用（`yq .key f.yaml`，不支持 `yq e`）。`xargs -I`、`du -b`、`bc` 不可用，`find -printf`、`find -exec wc -c {} +`、`comm`、`join`、`awk` 数组、`sort -rn`、`uniq -c` 可用。

## 自检
- build.py 连跑两次逐字节一致（改题面后重跑再比对一致）。
- `gate.sh v2.1 '*-322[0-5]?'`：lint 0 违规，verify 50/50（含 sabotage）。
- `corpus loadcheck`：全目录 560 题加载通过，本批 50 题无错。

## 已知风险
- 写文件题 equals 严格到末尾换行与排序规则；老师用 write_file 写出无末尾换行会判错（题面已说明一行一条，但没有显式提换行）。
- e2/e8 的参考命令最后 `echo 3`（题面里就是前 3 名 / 3 个队），属沙箱核对用的占位，不影响题目。
- 排序用 `sort`（字节序）；中文目录名的排序在 e5 依赖 C 序，老师若按拼音排会错。
- 部分题（a2/a3/a9）有“第二名接近”的断言，但差距只保证 >0 或 >500。
- fixture 最大约 100KB 级（JSONL 700+ 行），read_file 64KB 截断本身就是考点之一。

## 老师最可能答错的 5 道
1. tab-32212（至少两条记录且平均分 ≥85 的学生数）：按行数或漏掉“至少两次”。
2. tab-32205（去重用户数 + props 缺失的第二问）：数事件数而不是人数，props 缺失处理错。
3. tab-32216（Platform 含全部嵌套子团队的 level≥5 人数）：只数顶层 employees，或 jq recurse 写错。
4. fs-32226（ORDER-7731 vs ORDER-77310）：grep 不带边界命中两个文件。
5. cfg-32231（顶层 enabled 与 tls.enabled、注释行）：grep "enabled: true" 把嵌套和注释数进去；第二问 awk 联合过滤出错。
