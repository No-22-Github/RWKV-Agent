# b21n 出题报告（v2.1 第三波，题号 33501–33570，共 70 题）

主题：小型代码仓库任务（每题 5–15 个短源文件，Python/JS/TS/Go/Shell/YAML/SQL 混合；沙箱 bash 无 python/node，不运行代码）。生成脚本 `bench/distill/tools/b21n/`（`common.py` 框架，`s1`–`s6` 各一个子类，`gen.py` 填充代码生成器）。

## 构成
- 子类：locate_definition 12（33501–12）、find_callers 12（33513–24）、count_markers 12（33525–36）、fix_edge_case 12（33537–48）、explain_readonly 11（33549–59）、report_test_result 11（33560–70）。
- 中文 47（67%）/ 英文 23；多轮（2 个用户轮）24（34%）；难度 L1 29 / L2 41，无 L0、无 L3。
- tool_policy：每题都写 `must_offer`（bash+read_file 17、list_files+read_file+write_file 17、search_text+read_lines+replace_lines 13、search_text+read_file 12、其余 11）；需要行号的题一定带 search_text / read_lines / bash；改文件题带成对写工具；解释和报告类题把 write_file 放进 must_offer 以便测"提供了也不写"。

## 判据设计
- 定位/行号题：`output_contains` 放文件路径 + 行号 + 值，行号由 fixture 现算（`lineno()`），含数字的轮次开 `output_contains_token`。
- 调用方题：只列路径，题面写"只回答文件路径，一行一个"，因此 `output_excludes` 可放注释/字符串/近名函数所在的文件（诚实回答不会列它们）；多轮里一半第二轮要求"把调用方也改掉"，用 `expect.files` equals 精确判结果，无关文件自动 unchanged。
- 计数题：答案是数字，范围限定（目录、vendor/docs/tests 排除、字符串与变量名里的 TODO 不算）写在题面；verify 用正则从 fixture 重算。
- 修 bug 题：全部 `expect.files` 逐文件 equals/unchanged（改动都是单 token 的边界修复，题面给出期望行为，修法唯一）；读回核对用"告诉我改了第几行"判（行号来自 fixture）；若干第二轮是只读追问（`forbidden_tools` 写工具）。
- 解释题：`forbidden_tools` = write_file/replace_lines/append_file，所有文件 unchanged；同时要求给出可由 fixture 推出的具体值（Python 题 verify 直接 exec fixture 算）。
- 测试日志题：日志是 fixture，含多次运行（TR-SUPERSEDE）、重试后通过、skip/ignore、名字里带 failed 的通过用例、XML/TAP/cargo/jest/go test/pytest 多种格式。
- 不用 `output_excludes` 的否定短语；英文关键词不依赖大小写。

## 沙箱实测
- build.py 末尾把参考命令（grep -rn / grep -rE / grep -rc / wc -l 等 20 余条）在 just-bash 里真跑，输出必须含正确答案。
- 每题 verify.py 先校验 fixture sha256，再从 fixture 重算答案（locate/callers/count 用正则，explain 用 exec/手写镜像，fix 重放 ops）。

## 自检
- build.py 连跑两次，70 题全部文件逐字节一致（sha1 对比）。
- `RWKV_LAB=local/bin/rwkv-lab-v21 gate.sh v2.1 'code-335[0-7]?'`：lint 0 违规，verify 70/70。
- `rwkv-lab-v21 corpus loadcheck --cases bench/distill/v2.1/cases`：1145 题加载通过。

## 已知风险
- 修 bug 题要求逐字 equals：老师若顺手改了空格、顺带"优化"或把比较写成等价但不同的形式会判错（题面已限定"只改那一处"）。
- 调用方/计数题的 fixture 是程序拼装的填充代码，命名风格有重复（行号、数字不同但结构相似）；去污染若撞题请直接删。
- 单位数字答案（如 "3"、"2"、"4"）靠 token 边界判，老师若写"三个"会漏判；题面多用阿拉伯数字回答的问法，未强制。
- 部分第二轮只读追问用 `output_contains_any` 词表（"没有/不需要/正确…"），中文同义说法可能漏收。

## 老师最可能答错的题
1. code-33514 / 33518 / 33520 / 33522 / 33524（多轮"把调用方也改掉"）：要先列调用方再逐处改，漏改一处或误改测试/文档文件即判错。
2. code-33538（movingAvg 与 pairs 循环头相同，只能改前一个）、code-33543（find 与 lower_bound 二分写法不同，只改 find）。
3. code-33564（同一日志两次运行，要以最后一次为准）和 code-33566（重试后通过的用例不算失败）。
4. code-33526 / 33527 / 33536 计数题：范围限定（去 legacy/old、排除测试文件、变量名不算）容易多数或少数。
5. code-33556（令牌桶两段时间的放行数）、code-33510（两个同名 retry，要选被 source 的那个）。
