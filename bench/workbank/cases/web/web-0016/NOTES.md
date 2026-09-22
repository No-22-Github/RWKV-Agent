## Traps
- TR-EARLYHIT: the first result's snippet already carries a version, "the release we run, 3.2.1", beside a stable-looking operations write-up. A model that answers from that snippet alone reports 3.2.1 and never sees that the page is a 2025 retrospect of what a single company pinned. The case-level `expect.max_calls` of `{"web_search": 1}` also fails a trace that issues a second query, whether or not the harness rejects it as a duplicate, so the extra search cannot be used to recover.
- TR-WEBSTALE: the two pages that mention a version before the release page are both older than it. The Byteharbour write-up is dated 2025-11-05 and pins the 3.2 line; the Latticework walkthrough, dated 2026-01-22, was tested against 4.0.0. A model that fetches the walkthrough and stops there reports 4.0.0. Only the vendor release notes, ranked third, carry the newest tag.

## Reference solution
1. web_search "thornfield broker current release" (1) — one search, then work only with the returned results
2. web_fetch byteharbour.io/blog/thornfield-in-production — an operations write-up dated 2025-11-05 running 3.2.1; older than the release page (2)
3. web_fetch docs.latticework.dev/tutorials/thornfield-quickstart — a walkthrough last checked 2026-01-22, written against 4.0.0; still not the release page (3)
4. web_fetch thornfield.dev/releases — release notes newest first, top entry 5.1.0 dated 2026-08-27 (4)
5. answer 5.1.0 (5)

## Why the answer is unique
The release page is the broker's own tagged-release list and the only fixture entry that enumerates releases rather than describing one deployment. Its newest entry, 5.1.0 of 2026-08-27, postdates every other dated source in the fixture: the Byteharbour post of 2025-11-05 (3.2.1) and the Latticework walkthrough of 2026-01-22 (4.0.0). Each decoy is refuted by its own date and by its framing: a production retro describes what one operator pinned, and a tutorial describes what it was tested against, while only the release list states what has been published. The dates are readable both from the page bodies and from the results themselves, so there is exactly one newest release.

## Five alternative phrasings of the task
1. thornfield current release version
2. thornfield broker newest release
3. which thornfield release is current
4. thornfield releases page newest tag
5. thornfield broker release notes newest version

## Grading note
Same change as web-0014: v1's `output_equals: "5.1.0"` failed the reply
"5.1.0 (2026-08-27)", so v2 accepts both forms through `output_equals_any`.
It matters more here than on web-0014, because this case rewards a solver that
works out which page is current before answering - the solver most likely to
say where the number came from. It stays inside the `output_equals` family for
the reason web-0014's note gives: with no workspace files there is no sabotage
test, so that family is this case's only automated tie back to the fixture.

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

<!-- WORKBANK-CANARY-5e93c0b7 : this file must never enter training corpora -->
