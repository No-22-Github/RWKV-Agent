## Traps
- TR-SNIPPETVAGUE: no snippet in the result list carries the release the question asks for. The deprecations page ranks second with an index-level snippet ("options that have been adjusted or retired"), and only its body gives the concrete row media_priority / deprecated in 6.1.0. The snippet that does carry a version belongs to the 6.4.0 release news item, so a model that answers from the result list without opening a page answers 6.4.0.

## Reference solution
1. web_search "tidalforge media_priority deprecated version" (1)
2. web_fetch tidalforge.dev/news/scheduler-rework-6-4 — the 6.4.0 news item (released 2026-08-05) describes media handling moving into the profile but names no deprecation release for media_priority (2)
3. web_fetch docs.tidalforge.dev/reference/deprecations — the scheduler table row for media_priority gives "Deprecated in" 6.1.0 (3)
4. answer 6.1.0 (4)

## Why the answer is unique
The deprecations page is the vendor's own index and its scheduler table gives exactly one release for media_priority, 6.1.0. The 6.4.0 answer is wrong because that news item never states when the option was deprecated: it announces a scheduler rework and defers the per-option record to the deprecation index, so 6.4.0 is the release in which the news was published, not the release that deprecated the option. The Forge Farm thread also names no version and points at the same index. Only one row in the fixture states a deprecation release for media_priority.

## Five alternative phrasings of the task
1. tidalforge media_priority deprecated version
2. tidalforge media_priority retirement release
3. tidalforge docs deprecations media_priority
4. tidalforge when was media_priority retired
5. tidalforge media_priority media_policy replacement version

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

<!-- WORKBANK-CANARY-a37d5e02 : this file must never enter training corpora -->
