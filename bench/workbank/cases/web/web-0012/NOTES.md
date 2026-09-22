## Traps
- TR-FETCHFAIL: the first search result advertises https://wiki.harborlight.io/errors/HL-3312, but that entry carries a `url` and no `url_match`, so a fetch of it returns the not-found body. A model that stops after the dead first link answers UNKNOWN.
- TR-DECOY: the second result is a community thread about HL-3132 (tidebreak), a transposed-digit neighbour of the requested HL-3312. It ranks above the vendor reference, its title repeats a live-looking code, and its snippet and body both spell out tidebreak, so a model that skims the prominent result reports the wrong code's condition. The usable answer is on the third result, docs.harborlight.io/reference/errors, where HL-3312 is moatleak.

## Reference solution
1. Search "harborlight error HL-3312" (1)
2. Fetch wiki.harborlight.io/errors/HL-3312 - the advertised wiki page is gone; the fetch yields the not-found body (2)
3. Fetch community.harborlight.io/t/hl-3132-keeps-recurring - it explains HL-3132 as tidebreak, a different code (3)
4. Fetch docs.harborlight.io/reference/errors - the table row for HL-3312 gives the condition name moatleak (4)
5. Answer moatleak (5)

## Why the answer is unique
The vendor reference is the only entry that names HL-3312, and it gives exactly one condition, moatleak ("the primary's write lease and the quorum's view disagree"). Its own table also lists HL-3132 as tidebreak, which confirms that the community thread's tidebreak belongs to the transposed code and not to the requested one. The dead wiki entry has no content; no other entry assigns a condition to HL-3312. The only two plausible errors are therefore answering UNKNOWN after the dead link, or echoing the adjacent code's tidebreak.

## Five alternative phrasings of the task
1. harborlight error HL-3312 meaning
2. what does harborlight HL-3312 mean
3. harborlight HL-3312 condition name
4. harborlight error reference HL-3312
5. harborlight cluster error HL-3312 documentation

## Grading note
`output_contains` is a case-sensitive raw substring, so v1's single lowercase
needle `moatleak` failed the answer "Moatleak" - the capitalisation a model reaches
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

<!-- WORKBANK-CANARY-cc41b7f2 : this file must never enter training corpora -->
