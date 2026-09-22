## Traps
- TR-WEBSTALE: the community recap page (ranks first, touched 2026-08-14 but only tracks the 1.x/2.x series) and the production blog (published_at 2025-10-14, ferrocache 2.6) both present 128 as the default. The vendor changelog ranks third; its 4.2.0 entry (2026-07-30) sets the default to 256. A model that stops at the recap or the blog answers 128.
- TR-SNIPPETVAGUE: no snippet states the current value; the recap's snippet dangles only "the original 64-shard layout". A model answering from the search results without opening any page grabs 64.

## Reference solution
1. web_search "ferrocache default shard_count" (1)
2. web_fetch cachefolk.net/ferrocache-shard-defaults — community recap: 1.x 64, 2.x 128, no current value (2)
3. web_fetch ferrumwheel.net/blog/ferrocache-shard-tuning — blog dated 2025-10-14, ferrocache 2.6 era, 128 (3)
4. web_fetch ferrocache.io/changelog — 4.2.0 (2026-07-30): "The default shard_count is now 256" (4)
5. answer 256 (5)

## Why the answer is unique
The changelog is the vendor's release history and its newest entry (4.2.0, 2026-07-30) states the current default in plain words ("is now 256"). The recap is a community page covering only the 1.x and 2.x series; the blog predates 4.2 and carries an in-content date and version. Dates are readable from published_at and from page content, so only one value can be the default of the current release.

## Five alternative phrasings of the task
1. ferrocache default shard_count
2. ferrocache shard count default value
3. how many shards does ferrocache create by default
4. ferrocache shard_count out-of-the-box setting
5. ferrocache docs default shard count

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

<!-- WORKBANK-CANARY-09d4f7b2 : this file must never enter training corpora -->
