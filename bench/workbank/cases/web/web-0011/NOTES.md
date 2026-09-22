## Traps
- TR-EARLYHIT: the first search result's snippet already states the answer outright ("TRD-1094 reports a coldshard: a cache region that never warmed after a worker restart"). One search is enough, so the case carries `expect.max_calls: {"web_search": 1}` (case-level, counted over the whole transcript): a second search call, including one the harness rejects as a duplicate, breaks the cap. The decoy a careless model lands on is hotloop: the same index page lists TRD-2211 (hotloop) above TRD-1094, and the second result is a thread about TRD-2211, so a model that distrusts the snippet and reads the top of the table instead of the named row reports the neighbouring code's condition.

## Reference solution
1. Search "tiderail error TRD-1094": the first result's snippet names the condition coldshard (1)
2. Answer coldshard (2)

## Why the answer is unique
The snippet and the index table both tie TRD-1094 to exactly one condition name, coldshard. The condition strings on that page are unique per code (TRD-2211 is hotloop, TRD-1088 is thinmoss), so hotloop is the name of a different code. The other results discuss TRD-2211 or probe tuning and never rename TRD-1094, so there is no second reading of the requested code.

## Five alternative phrasings of the task
1. tiderail TRD-1094 meaning
2. what does tiderail error TRD-1094 indicate
3. tiderail TRD-1094 condition name
4. tiderail error index TRD-1094 explained
5. tiderail TRD-1094 documentation

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `coldshard` failed the answer "Coldshard" - the capitalisation a model reaches
for when the term opens its reply. v2 uses `output_contains_any` with the
lowercase, capitalised and upper-case forms. The vendor term itself is
unchanged; only the spelling tolerance is.

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

<!-- WORKBANK-CANARY-5f0a93d1 : this file must never enter training corpora -->
