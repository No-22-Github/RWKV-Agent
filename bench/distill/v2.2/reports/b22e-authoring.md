# b22e 出题报告（v2.2，题号 34401–34450，共 50 题）

主题：大文件先看规模（wc/head），再用 grep/awk/sort|uniq 定位或统计；需要原文时用 grep -n 的行号加 read_file 的 start_line。生成脚本 `bench/distill/tools/b22e/`（工具目录 work-v3，13 个工具）。

## 构成
- 子类：E1 大日志 25（log-34401–34425）、E2 大表格 15（tab-34426–34440）、E3 大目录 10（fs-34441–34450）。
- 其中 E1 有 8 题要先 grep 出行号再读上下文（34404、34409、34412、34413、34416、34421、34422、34424），首轮 `required_tools` 为 `["bash", "read_file"]`。
- 中英：中文 32（64%）/ 英文 18。分子类：E1 15/10，E2 9/6，E3 7/3。
- 多轮（2 个用户轮）19（38%）：E1 8，E2 7，E3 4。无 L0；难度 L1 46、L2 4（每题声明 TR-TRUNC 一个陷阱）。
- 平均题面字数（按轮）：E1 63、E2 57、E3 52。
- tool_policy：日志、表格 `must_offer: [bash, read_file]`；目录 `must_offer: [bash, list_files]`。都不写 never_offer（计算器、data_query 若被提供也不挡，通过判据只看是否用了 bash）。

## 数据规模（build.py 里有断言）
- 日志 2100–3800 行（最大 358KB，行长 ≤120 字符），格式有 nginx 访问日志、syslog、应用日志、JSON lines、中文级别日志、CI 日志、cron、数据库慢查询共 8 种，时间戳连续，错误行零散植入。
- 表格 2101–3601 行（≤156KB），含分号分隔、带引号的逗号字段、两个月份文件。
- 目录 305–340 个文件（≤295KB），分 4–6 个子目录，文件大小、扩展名、头部日期都有分布。
- 答案要么在第 200 行之后（定位类，生成时断言答案不在前 200 行），要么需要全文统计（计数、求和、分组、去重）。

## 判据设计
- 首轮 `required_tools: ["bash"]`；case 级 `expect.max_calls: {"read_file": 3}`。
- 数字题 `output_contains_any`（含千分位与去尾零写法）+ `output_contains_any_token`；字符串题 `output_contains`，含纯数字时开 `output_contains_token`。
- 没写 `output_excludes`：错误答案是各种随机数，写不全，靠答案正确性判。
- verify.py 先校验 fixture 的 sha256，再从 fixture 重新算答案。NOTES.md 写明陷阱、参考命令和答案。

## 沙箱实测
- 每题的参考 bash 命令（合计约 60 条）在 just-bash sidecar 里真跑，输出必须含正确答案，每次构建都跑。
- 用到的命令均实测可用：`grep -n/-c/-o/-rl`、`awk` 数组聚合、`sort -k -nr`、`uniq -c/-d`、`cut`、`sed -n` 与 `sed` 替换、`find -printf '%s %p'`、`find -size 0`、`md5sum`、`xargs cat`。`awk -F';'` 用于分号文件。

## 自检
- build.py 连跑两次，50 题文件逐字节一致（用 shasum 比较两次的全部输出）。
- `gate.sh v2.2 '*-344[0-5][0-9]'`：50 case(s) checked, 0 violation(s)；verify 50 / 50。
- `corpus loadcheck`：331 case(s) load。

## 每个子类的两种“走错方向”答法
- E1：（1）只读第一屏 200 行就答“没有 502”或随口给个时间，或者一屏一屏翻（第 4 次 read_file 触发 `max_calls`）；判据靠答案不在前 200 行，答不出正确时间或行号。（2）grep 到行号后凭印象写前后文，没读上下文就报任务编号，答案对不上（8 题要求 read_file）。
- E2：（1）没跳过表头或没按分隔符拆（分号文件用逗号 cut，带引号的备注列错位），汇总值不对。（2）只看前几十行的头部数据就报“最高的区域”，数字或名称不对，且没有 bash。
- E3：（1）list_files 默认只给 200 条，用截断后的列表数 png 或找最大文件，数字或文件名错。（2）把文件修改时间当“更新日期”（题目日期在文件内容或文件名里），数字错。

## 已知风险
- 老师（千问 3.7 Flash）可能不用 bash 而用 search_text、list_files 配 read_file 得出答案，此时 `required_tools: ["bash"]` 会判不过；这是本批想教的行为，通过率可能偏低。
- 8 个上下文题要求 read_file；老师若用 `grep -B/-A` 或 `sed -n` 看上下文，会因没调 read_file 判不过。
- 少数题答案比较长（如 34403 要报错内容加次数，34423 去重计数），表述不同会影响 token 判据；已尽量用短答案。
- 部分题（`deep=False`，约 30 题）的答案字符串（区域名、服务名）出现在前 200 行，靠全文统计保证不能只看第一屏；单看答案不能排除“碰巧蒙对”。
- fixture 全部由程序生成（固定种子），消息模板有重复，去污染若撞题请直接删。

## 我认为老师最可能答错的题
1. log-34403：五类报错接近，要同时报内容和次数。
2. log-34423：去重错误码，容易数行数而不是去重数。
3. fs-34448：按内容去重，需要 md5sum，沙箱里 `find -exec md5sum {} +` 才通。
4. tab-34436：带引号的逗号字段，需要用 `$NF`。
5. log-34422：要取“最后一次”重启的前一条，容易取第一次。

## 去污染返修（验收后）
- 11 题撞名：日志文件改为带业务含义的名字（如 logs/edge-proxy-0913.log、logs/mesh-sidecar-0911.log、logs/订单中台-0915.log、logs/shop-front.log(.1)），34410 题面换了问法；tab-34428/34432/34439 换了文件名和列名（member_no、settle_state/gross、unit/monthly_pay）。
- 重跑：build 两次一致，gate 0 violation、verify 50/50，loadcheck 通过，七个测试集 decontam 均 0 flagged。
