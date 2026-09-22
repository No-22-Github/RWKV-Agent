## Traps
- TR-FETCHFAIL: the first search result (a community wiki entry titled "copperlane CL-5812", ranks first with a promising snippet) is advertised with a URL that has no resolvable page, so fetching it returns the not-found body. The fixture entry deliberately carries a `url` but no `url_match`. A model that gives up after the dead first link answers UNKNOWN. The working vendor reference ranks second and names the condition.

## Reference solution
1. Search "copperlane error CL-5812" (1)
2. Fetch wiki.copperlane.io/errors/CL-5812 - the advertised wiki page is gone; the fetch yields the not-found body (2)
3. Fetch docs.copperlane.io/reference/errors - the table row for CL-5812 gives the condition name ledgerdrift (3)
4. Answer ledgerdrift (4)

## Why the answer is unique
The vendor error reference is the only fixture entry that assigns a condition name to CL-5812: ledgerdrift, "the posted ledger entries no longer reconcile against the settlement file". The community wiki entry has no reachable page and no content, and the status-page incident names no code. The other codes in the reference table carry different condition names (latefeed, gatehold, thincover), so the reply cannot be one of those without a misread of the row.

## Five alternative phrasings of the task
1. copperlane error CL-5812 meaning
2. what does copperlane CL-5812 mean
3. copperlane settlement error CL-5812 condition
4. copperlane error reference CL-5812
5. copperlane CL-5812 documentation name

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `ledgerdrift` failed the answer "Ledgerdrift" - the capitalisation a model reaches
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

<!-- WORKBANK-CANARY-b62d8e04 : this file must never enter training corpora -->
