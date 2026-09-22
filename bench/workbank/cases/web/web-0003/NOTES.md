## Traps
- TR-FETCHFAIL: the first search result (community wiki, ranks first with a promising title and snippet) is a stale index entry; fetching its URL returns a "Page not found" body because the wiki page was removed. A model that gives up after the dead first link answers UNKNOWN. The working documentation page ranks second and carries the answer.

## Reference solution
1. web_search "quillmark serve default port" (1)
2. web_fetch wiki.quillmark.io/configuration — returns a page-not-found body (2)
3. web_fetch docs.quillmark.dev/reference/serve/ — the options table lists --port with default 8630 (3)
4. answer 8630 (4)

## Why the answer is unique
The serve command reference is the vendor documentation page; its options table marks --port with default 8630. The wiki entry carries no value (its page is gone), and the GitHub issue discusses the port-collision fallback without naming the default, pointing at the same reference page. No other fixture entry states a port value.

## Five alternative phrasings of the task
1. quillmark serve default port
2. quillmark preview server default port number
3. what port does quillmark serve use by default
4. quillmark docs serve port default value
5. quillmark preview server port setting default

## Grading note
两处改动（本轮）。

`expect.required_tools: ["web_search"]`：这道题没有任何工作区文件，题面也不含 URL，
所以答案只可能来自一次检索。加这条不改变模型的行为，也不改变通过与否——没检索的运行
本来就答不出来——它改的是**归因**：失败信息变成 `required tool "web_search" was not called`，
`capability_gate` 据此把它记进 `toolchoice` 层而不是 `capability` 层，能力读数不再被
"模型没出门"污染。

题面补了一句"本地没有"的上下文：工作区是空的，而系统提示词第一句是
`You are a local-first assistant`，模型 `list_files` 看到空目录后按 UNKNOWN 契约退出，
从它的角度是守规矩。真实用户问这种问题时会先说一句"我们自己没有"，补的就是这句任务上下文
——不是工具暗示（题面出现工具名会被 lint 拦下）。

**这句话能不能奏效，本轮数据没有给出把握。** 证据是 Qwen3.5-9B 三轮温度 0、题面一字不变，
16 道 web 里有 9 道在"搜/不搜"之间抖动（每轮都恰好搜 7 道，但搜的是不同的 7 道）；
而 web-0001 与 web-0002 句式几乎相同却长期一搜一不搜。也就是说这个行为本来就在临界点上
左右摇摆，不是措辞驱动的。补上下文是把偏置往正确方向推一点，真正的压力来自系统提示词的
local-first 框架——那要改就得动 work-v1 的 wire，影响全库 148 题与全部历史跑分，
本轮按「先 C+A，不够再动系统提示词」的次序留着。

<!-- WORKBANK-CANARY-c5813e6a : this file must never enter training corpora -->
