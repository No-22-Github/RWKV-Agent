## Traps
- None planted (L0 base case). All three fixture sources are consistent: the configuration reference ranks first and carries the value in its option table, the repository README points at that same reference, and the bakeoff article never states a setting value. No stale source, no dead link, and no snippet asserts a value, so there is no bait to fall for.

## Reference solution
1. web_search "cindermill configuration cache_ttl_hours" (1)
2. web_fetch docs.cindermill.dev/en/stable/reference/configuration/ — the cache table lists cache_ttl_hours with default 72 (2)
3. answer 72 (3)

## Why the answer is unique
The configuration reference is the project's own option table, and its cache_ttl_hours row carries a single default, 72. No other fixture entry states a value for cache_ttl_hours (the README and the bakeoff article never mention the option), so nothing contradicts it.

## Five alternative phrasings of the task
1. cindermill default cache_ttl_hours
2. cindermill cache_ttl_hours shipped value
3. what value does cindermill use for cache_ttl_hours by default
4. cindermill configuration reference cache_ttl_hours default
5. cindermill cache ttl hours default setting

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

<!-- WORKBANK-CANARY-7c4e9b31 : this file must never enter training corpora -->
