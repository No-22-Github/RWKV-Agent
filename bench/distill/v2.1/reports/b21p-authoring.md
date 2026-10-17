# b21p 出题报告（v2.1 第三波，题号 33701–33770，共 70 题）

生成脚本 `bench/distill/tools/b21p/`。文件系统 35 题（fs-33701–33735），日志 35 题（log-33736–33770）。

## 构成
- 子类：largest 6、duplicates 6、count_by_type 6、presence 5、scoped_delete 7、按大小/修改时间/内容找文件 5；root_cause 9、time_window 9、locate_error 8、count_events 9。
- 中文 45（64%）/ 英文 25；多轮 41（59%）。难度：L1 12 / L2 58，L0 0。
- tool_policy：全部写了 `must_offer`（bash+read_file 为主；scoped_delete 要求 bash；窗口题 w6 要 bash+datetime），没有 never_offer。因为这些题的通过路径都依赖 bash，所以没有留“不约束”的题；比任务书建议的“一半不约束”偏紧。
- scoped_delete 用 `expect.files`（被删的 absent、其余 unchanged）+ `required_tools: bash`；删除类首轮不设确认，范围写得很明确。

## 判据与数据
- 数值答案 ≤ 3 位的开 `output_contains_token`；1000 以上的数（2470）同时收 `2470/2,470`。
- 诚实“不存在/没有重复”的轮次用 `output_contains_any` 词表（中英、大小写、弯引号），不放 `output_excludes`。
- 日志 150–250 行短行；count/window 题的 fixture 都由结构生成，答案在脚本里重算，`verify.py` 另用独立写法（切分/正则）复算。
- 陷阱：深层嵌套、隐藏目录、同名/同大小不同内容、大小写扩展名、.bak/.old 近名、跨午夜与时区窗口（UTC vs 北京时间、epoch 秒、dd/mm/yyyy）、半开区间边界、INFO 行里的 ERROR 字样、FATAL 先于 ERROR、轮转日志里更早的错误、多文件根因。
- 沙箱实测要点：`uniq -w`、`ls --time-style`、`cksum` 不可用（重复文件用 `sha256sum | sort | awk` 分组）；`awk -F.` 要写 `-F'[.]'`；`find -printf '%s %p'` 可用。

## 自检
- build.py 连跑两次，70 题全部文件 shasum 一致。
- `gate.sh v2.1 '*-337[0-7]?'`：lint 70 题 0 违规，verify 70/70。
- `corpus loadcheck`：1134 题全部加载通过。

## 已知风险
- 根因题的第一轮用“原因关键词 + 时间”判，老师若答对原因但只写 HH:MM:SS 之外的格式（如“2 点 41”）会误判。
- mtime 无法在 fixture 里设置，“按修改时间筛选”用带日期的清单文件（inventory/listing）代替。
- 多数题强依赖 bash；若训练时目录随机缺 bash，则这些题不会被抽到（must_offer 已保证）。
- 布局上模板化的 fixture 生成器较多，去污染撞题请直接删。

## 老师最可能答错的题
1. fs-33710：三份同名同大小、仅一字符不同的文件，容易误报重复，或在“没有重复”时编造一组。
2. fs-33731/33732：阈值紧贴（1960、99 字节），若用 `ls -S` 或块大小的 `find -size +2k` 会错。
3. log-33745、33747：UTC 与北京时间换算，前一天的日期容易算错，33747 两个文件用不同窗口。
4. log-33748：epoch 秒日志，沙箱里没有 awk strftime，要用 `date -d` 换算。
5. log-33752：半开区间，12:30:00 的事件必须排除。
6. log-33760/33756：先出错的服务/轮转文件在“看起来次要”的一方，只读主文件会错。
7. log-33743（时钟回拨）、33739（交换机抖动）根因离症状最远，老师易停在 401/SERVFAIL 层。
8. fs-33726/33730：先列后删的多轮，易在第一轮提前删除。
