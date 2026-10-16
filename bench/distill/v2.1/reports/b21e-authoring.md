# b21e 出题报告（v2.1 tabular：用 bash 算准表格数据）

题号 tab-32001–32050，共 50 题，脚本 `bench/distill/tools/b21e/`（`build.py` + `common.py` + `s_count/s_group/s_top/s_multi/s_write.py`，固定种子，重跑逐字节一致）。

## 分布
- 子类：按条件计数 12（32001–32012）、分组求和/均值 12（32013–32024）、去重计数与 top-N 10（32025–32034）、多条件筛选 8（32035–32042）、算完写 CSV 8（32043–32050，全部 expect.files equals，源文件 unchanged）。
- 中英：中文 27 / 英文 23（54%）。多轮 16（32%）。难度 L1 46、L2 4（L0 无）。
- tool_policy：must_offer 全含 bash + read_file；17 题（34%）加 never_offer calculator、data_query，其余不限制。
- 表规模 210–600 行，题面都是一句话统计问题。每题 1–2 个“先看表头才不会错”的点：近名列（amount/amount_refunded、商品金额/退款金额）、带引号含逗号字段、千分位引号数字、TSV、首行 `#` 注释、末尾空行、含空格表头、列顺序不寻常、日期 MM/DD/YYYY、状态值互含（未还/逾期未还、及格/不及格）。

## 判据设计
- 数值答案：`output_contains_any`（原值、千分位、去尾零写法）+ `output_contains_any_token`；整数答案 20–130 为主，已避免 0 和个位数答案。
- top-N 答案：`output_contains` 全部名字 + `output_contains_token`；构造时断言边界无并列。
- 写文件：`expect.files` equals 整个 CSV（含表头、排序、小数位），题面写清文件名、表头、排序、小数位。
- 没写 `output_excludes`（错误数值无法穷举）；没加 `max_output_chars`；题面不点工具名。
- 每题 verify.py 先校验 fixture sha256，再用 python csv 从 fixture 重算；用的计算源码与 build.py 共用。

## 参考命令已在沙箱真跑
build.py 对每题每一轮的 bash 参考命令（head 看表头 → awk/sed/sort/uniq 计算，写文件题含 printf 表头 + awk >> 输出）用 Sidecar 在 just-bash 里真跑：数值题要求 stdout 出现 python 重算的主形式，top-N 要求名字按序出现，写文件题用 sidecar `read` 读回覆盖层文件并与期望字节级一致；不一致则 build 失败。沙箱实测可用：awk（无 FPAT）、sed -E（含 `:a;...;ta` 循环）、sort（无 -g，用 -rn）、uniq -c、cut、head、wc、printf、tr；没有 bc。

## 自检
- build.py 连跑两次，cases/tabular 目录 diff 逐字节一致。
- gate.sh v2.1 'tab-320[0-5]?'：lint 0 违规，verify 50/50。
- corpus loadcheck 560 题全部加载，无错误。

## 已知风险
- 均值/求和用 awk 与 python 的 `%.Nf` 对账，已在 build 中逐题核对；个别模型用四舍五入到不同位数会判错（题面均写明小数位）。
- top-N 只判名字，不判次数；先后顺序不判（只要求全含）。
- 未写 excludes，错误的“说没有”靠数值 token 判。
- 并行批次(b21f–h)的题与本批同目录；loadcheck 本批无错。
- 题族内模板相近（同类计数题结构相似），但主题、列名、数据、数值均不同。

## 老师最可能答错的 5 道
1. tab-32017：引号逗号摘要 + 千分位金额叠加，需两遍 sed 清洗，直接 awk 必错。
2. tab-32038：日期 MM/DD/YYYY + 千分位 + 三条件，月份取错或漏清洗。
3. tab-32048：写 failed 行原样复制 + 第二轮按 reason 计数，`disk full` 含空格，awk 默认分隔会拆开，killed 行需排除。
4. tab-32047：同一用户多行，需“城市+用户”先去重再数，容易数行。
5. tab-32045：两个文件的格式（原样保留列、金额降序、两位小数）细节多，列/排序易错。
