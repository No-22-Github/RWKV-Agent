## Traps
- TR-SUPERSEDE: the community option history (in-content date 2026-01-14, covering the 8.x line) says session_ttl_minutes was deprecated in 8.5.0, while the vendor's release notes record the deprecation under 9.3.0 (released 2026-07-09). A model that takes the community page's release answers 8.5.0. Dates are readable from the page bodies (the "last touched" line and the release-day dates), not from the URLs.
- TR-SNIPPETVAGUE: neither page that carries a deprecation release states one in its snippet. The community page's snippet says only that options "changed across the 8.x line", and the release notes' snippet says only that it covers the 8.x and 9.x series. The only snippet containing a version belongs to the 9.5.0 news item, so a model that answers from the result list grabs 9.5.0.

## Reference solution
1. web_search "marrowgate session_ttl_minutes deprecated version" (1)
2. web_fetch authwiki.net/marrowgate-option-history — community page last touched 2026-01-14, claims the deprecation landed in 8.5.0 (2)
3. web_fetch marrowgate.io/news/passkeys-in-9-5 — the 9.5.0 news item (released 2026-08-28) names no deprecation release for session_ttl_minutes (3)
4. web_fetch docs.marrowgate.io/release-notes — the 9.3.0 entry (2026-07-09) deprecates session_ttl_minutes; the 9.5.0 entry (2026-08-28) does not (4)
5. answer 9.3.0 (5)

## Why the answer is unique
The release notes are the vendor's record of what each release did, and their 9.3.0 entry states that session_ttl_minutes is deprecated in 9.3.0. The 8.5.0 answer is wrong on two counts: the community page is dated 2026-01-14 and covers only the 8.x line, and the vendor's own notes list 9.0.0 (2026-02-03) and 9.3.0 with no 8.5.0 deprecation entry at all, so no page but the community one asserts 8.5.0. The 9.5.0 answer is wrong because the news item is about passkey sign-in: its version is the release date of the announcement, and it explicitly defers the per-key record to the release notes. Only one entry in the fixture states a deprecation release for session_ttl_minutes.

## Five alternative phrasings of the task
1. marrowgate session_ttl_minutes deprecated version
2. marrowgate session_ttl_minutes retirement release
3. marrowgate release notes session_ttl_minutes
4. marrowgate when was session_ttl_minutes deprecated
5. marrowgate session idle_timeout replacement version

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

<!-- WORKBANK-CANARY-91c40fb6 : this file must never enter training corpora -->
