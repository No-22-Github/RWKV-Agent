## Traps
- None declared. This is the family's L0 baseline: one search, the vendor reference names the condition, one answer. Every fixture entry that touches the code agrees with the reference, so no careless reading yields a different condition name. The forum thread and the quarterly review are unrelated context, not decoys.

## Reference solution
1. Search "kelpgate error code KG-4021" (1)
2. Open docs.kelpgate.dev/reference/error-codes; the client-and-handshake table row for KG-4021 gives the condition name sealbreak (2)
3. Answer sealbreak (3)

## Why the answer is unique
Only the vendor reference states what KG-4021 reports, and it assigns exactly one condition name, sealbreak ("the upstream peer closed the connection partway through the TLS handshake"). The forum thread describes the same behaviour without naming it and explicitly defers to the reference page; the quarterly review says no code meaning changed and names none. No other fixture entry contains the string sealbreak or a competing name for KG-4021.

## Five alternative phrasings of the task
1. kelpgate error code KG-4021 meaning
2. what does kelpgate error KG-4021 indicate
3. kelpgate KG-4021 condition name
4. kelpgate gateway error KG-4021 explained
5. kelpgate error reference KG-4021

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `sealbreak` failed the answer "Sealbreak" - the capitalisation a model reaches
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

<!-- WORKBANK-CANARY-3a7f1c9e : this file must never enter training corpora -->
