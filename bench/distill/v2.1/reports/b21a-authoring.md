# b21a 出题报告（改已有文件，31001–31075）

## 概况
- 75 题，每题独立题族 `b21a-<子类>-<序号>`。生成脚本 `bench/distill/tools/b21a/`，无随机数，两次运行逐字节一致。
- 子类：定点改值 20（cfg/doc/code/fs 混合）、追加 vs 覆盖 12、多处一致修改 13、遵守排除说明 12、改完核对 18。
- 场景：cfg 约 23、doc 约 16、code 约 12、fs 约 9、tab 约 7（含 csv）、无 hybrid/logs。
- 中文题面 60/75（80%）；多轮 26/75（34.7%）；L0 为 0；L1 22 / L2 43 / L3 10。
- tool_policy：75 题全部写 must_offer（完整通过路径）：bash 19、read_lines+replace_lines 19、read_file+write_file 18、read_lines+write_file 14、read_file+append_file 5；never_offer 均含 web_*。

## 判据设计
- 改值/多文件/排除/核对题：`expect.files` 对改动文件用 `equals`（整文件精确），其余文件 `unchanged`（排除文件、协同文件、README 都被钉住）。verify.py 用同一份 op 列表从 fixture 重算，先校验 fixture sha256。
- 追加题：改为 `contains`（原文整体 + 每条新行），避免行尾换行差异误判，又能抓覆盖（原文丢失）。题面逐字给出要追加的行。
- 终答：`output_contains` 要求提到新值或改动位置；多处核对题要求复述最终内容，避免“已完成”空话。没有写字数上限。
- 数字类 output_contains（如“3”）是子串匹配、较弱，主要判据在文件。

## 已知风险
1. `equals` 是整文件字节比较：模型用 write_file 重写时若丢掉末尾换行会判错（replace_lines/bash 不会）。
2. 无法判“是否读回核对”：判据只能看结果与终答复述；读回行为靠题面要求和老师自然行为，需抽检轨迹。
3. （已处理）全部题 must_offer 含读+写路径；build 断言 equals 文件的末尾换行与 fixture 一致。
4. 排除类 31051（toc 自动生成）要求老师说明如何重新生成，终答只由 `toc` 子串判。
5. 31055/31056 第二轮说“所有文件都改”，按 README 应跳过 secrets/replica；若用户明说要改则另当别论，这里是泛指。
6. 没有用 bash sidecar 回放参考解（只靠 op 重算），参考解步骤写在各题 NOTES.md。
7. loadcheck 全树 245 题全部通过（含别批次）。

## 老师最可能答错的 5 题
- cfg-31064：两轮，插入一行后行号漂移，且 queue/dead_letter 的 retry 块重复。
- cfg-31062：toml 数组加 sg + 第二轮改上方的 flag（引号与逗号）。
- doc-31065：整表加一列，分隔行与空单元格 `|  |` 精确格式（equals）。
- cfg-31055：第二轮“所有环境文件”，需按 README 跳过 secrets.env 并如实说明。
- cfg-31075：删最后一项后前一项逗号必须去掉，再改另一条（equals）。

## 自检
- `python3 build.py` 连跑两次，cases 目录 diff 无差异。
- `gate.sh v2.1 '*-310[0-7]?'`：75 cases checked, 0 violation(s)；verify 75 / 75。
- `corpus loadcheck --cases bench/distill/v2.1/cases`：245 cases load，无错误。
