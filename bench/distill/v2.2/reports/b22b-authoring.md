# b22b 出题报告（v2.2，题号 web-34101–34150，共 50 题）

主题：用户消息里有完整网址时，用 web_fetch 读它，不把网址当文件路径，不说"没有网页工具"；网址读不到时如实说；网址加本地文件一起用。生成脚本 `bench/distill/tools/b22b/`（工具目录 work-v3）。

## 构成
| 子类 | 题数 | 中文 | 多轮 | 首轮题面平均字数 |
|---|---:|---:|---:|---:|
| B1 给网址直接读 | 30 | 15 | 11 | 86 |
| B2 网址打不开 | 10 | 5 | 2 | 75 |
| B3 网址 + 本地文件 | 10 | 7 | 3 | 97 |
| 合计 | 50 | 27（54%） | 16（32%） | |

难度：L1 49、L0 1（34106 无陷阱）。task_type：lookup_value、summarize_page、error_meaning、latest_version、deprecation、compare_sources。三个子类不是正反对照，所以中英、字数只在子类间比较：B1 与 B2 接近，B3 因带文件说明略长。

## 网址形态与位置
形态：https/http、带路径、.html、查询串（`?id=`、`?code=&lang=`、`?page=2`、`?serves=4`）、锚点（`#section-3`、`#overweight`、`#card`、`#post-14`）、端口 `:8080`、尾斜杠、大小写混用（34123）、无协议头（34126）、markdown 链接、尖括号、中英文括号包住、后跟句号。
位置：开头、中间、结尾、单独一行、一轮两个网址（34115）、第二轮才给网址（34109、34120、34136）。同路径不同查询串的两页互为干扰（34112、34125、34105）。34128 的第一个网址只是"已搬到新地址"的指针，必须跟随页面里的新网址再抓一次。

## 判据设计
- B1：`required_tools: ["web_fetch"]`（只在需要新抓取的轮次要求，追问同页的轮次不要求）；`forbidden_tools: ["read_file","search_text"]`；`output_excludes` 收"没有上网/无法访问网页/cannot browse/no web access"等64 个中英文说法；4 题（34101、34102、34109、34114）另放一个只能通过搜索得到的旧页面或第三方页面，`output_excludes` 放它的值。`output_contains` 放页面独有的值，裸数字开 token。
- B2：`required_tools: ["web_fetch"]`，`output_contains_any` 收"打不开/无法访问/失败/读不到/没有内容/not accessible/failed/unavailable/blank/empty"等235 个说法；案级 `max_calls: {"web_fetch": 3}`。7 题 fixture 里没有该网址（实际返回空正文加中文 note：页面读不到、不要编造，见 `emptyWebFetchNote`），3 题（34133、34135、34138）fixture 条目带 error，模拟超时、502、连接重置。34134、34139 在搜索里放了第三方页面；34139 第二轮要求"说明来源不是官方页"。34136 第二轮给镜像网址，可正常读。
- B3：`required_tools: ["web_fetch","read_file"]`；改文件的用 `expect.files.equals`（只改一行，其余不动；其他文件 unchanged），检查类的文件 unchanged。34147 第一轮是纯本地问题，`forbidden_tools: [web_fetch, web_search]`，第二轮才上网；34150 追加文件后 `review_before: accept`，第二轮读回。
- 所有页面 < 3000 token，整页返回，不触发 `.web/` 存档，所以 B1 禁用 read_file 是成立的。
- `verify.py` 校验 fixture sha256，答案值须出现在页面、文件或题面里（派生值如差值单独声明）；B3 编辑题由 verify 重算最终文件。

## 沙箱与自检
- `python3 build.py` 连跑两次，`cases/` 下所有文件 sha 逐字节一致。
- `gate.sh v2.2 '*-341[0-5][0-9]'`：
  ```
  50 case(s) checked, 0 violation(s)
  verify 50 / 50
  ```
- `rwkv-lab-v3 corpus loadcheck --cases bench/distill/v2.2/cases`：`loadcheck: 193 case(s) load`（含其他批次）。

## 每个子类的"走错方向"答法
- B1：(1) 把网址当路径调 read_file / search_text，被 `forbidden_tools` 判不过；(2) 回答"我没有上网工具，无法读取该页面"，词表命中 `output_excludes`，且没有 web_fetch 调用，`required_tools` 不过。另：搜索到旧页面就作答（如 34101 答 30 天），`output_excludes` 命中；只凭网址文字猜值，`output_contains` 不过。
- B2：(1) 页面空了仍编出具体内容（如 34131 编出票价涨幅），既没有"读不到"类词，`output_contains_any` 不过；(2) 一个网址反复抓五六次，`max_calls` 超 3；还有根本不调 web_fetch 直接说打不开，`required_tools` 不过。
- B3：(1) 只读网页不看本地文件，34141 答不出超标项，`required_tools` 与 `output_contains` 不过；(2) 改文件时把整个文件重写或多改一行（34149 连提现手续费一起改），`expect.files.equals` 不过；34147 第一轮就上网，`forbidden_tools` 不过。

## 已知风险
- 没有跑老师，所有"该怎么答"靠 fixture 与词表推演；B2 的词表即便很宽，仍可能漏收诚实但少见的说法。
- B1 禁用 read_file/search_text 对"先 list_files 再抓网页"不设限，属有意放宽。
- 网址里的大小写、查询串、锚点依赖 fixture 的子串匹配；模型若改写网址（丢掉 `?page=2` 等）会抓到空页。
- 34128、34139 需要两次以上调用，老师若一次就停会失败，但这是目标行为。
- 大部分页面只有一个关键值，属 L1 难度；L0 仅 1 题。
- 题面里有少量域名带 `-example`、`.example` 的虚构站点；去污染若撞题请整题删除。

## 老师（千问 3.7 Flash）最可能答错的题
1. web-34128：第一个网址只是搬迁提示，容易直接答"页面没写"，不去抓新网址。
2. web-34139：第二轮要说清第三方评测不是官方页，容易只报 92 分钟而不说来源。
3. web-34147：第一轮是纯本地问题，容易顺手上网。
4. web-34126：无协议头的网址要补 `https://`，容易当文件路径。
5. web-34112 / 34125：同路径不同查询串，容易抓成另一页。
