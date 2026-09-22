## Traps
- TR-LONG: the target page, docs.bellwether.dev/operating/sizing-and-limits, runs about 4,700 words (roughly 27.7 KB, an estimated 5,100-7,200 tokens), well past the fetch compression threshold, and the value is named exactly once, inside the prose sentence "The shipped default for max_concurrent_evaluations is 640 per node" in the Concurrency limits subsection. The page carries a dense Limits reference table near the end whose first row is a different concurrency setting, max_concurrent_publishes at 512; a model that works from a shortened view of the page, or that skims the table instead of reading the section that names the setting, reports 512.

## Reference solution
1. web_search "bellwether max_concurrent_evaluations default" (1)
2. web_fetch docs.bellwether.dev/operating/sizing-and-limits — read the Evaluation throughput section; the Concurrency limits subsection states the shipped default is 640 per node, and no other passage names a value for this setting (2)
3. answer 640 (3)

## Why the answer is unique
The operations guide is the only fixture entry that documents this setting, and within it the string 640 occurs exactly once, in the sentence that names max_concurrent_evaluations. The 512 that a skimmer may pick up belongs to max_concurrent_publishes, a different setting with its own row in the Limits reference table, and the changelog and forum thread do not state any default at all. A reader who follows the setting name to its sentence cannot reach any value other than 640.

## Five alternative phrasings of the task
1. bellwether max_concurrent_evaluations default
2. bellwether shipped value for max_concurrent_evaluations
3. what is bellwether's default max_concurrent_evaluations
4. bellwether operations guide max_concurrent_evaluations default
5. bellwether evaluator concurrency limit default

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

<!-- WORKBANK-CANARY-a1d74e28 : this file must never enter training corpora -->
