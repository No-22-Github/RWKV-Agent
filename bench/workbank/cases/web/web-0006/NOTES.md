## Traps
- TR-SUPERSEDE: two fixture pages give a different release for the same event. The migration post "Moving off analyzer_chain" (in-content date 2025-12-08) says analyzer_chain was deprecated in 3.9.0; the project's own release notes (newest entry 4.2.0, released 2026-06-23) record the deprecation under 4.2.0 and list 3.9.0 (2025-11-30) as an unrelated release. A model that takes the older, more directly worded page answers 3.9.0. The dates are readable from the page bodies (the post's byline date and the release-day dates in the notes), not from the URLs.

## Reference solution
1. web_search "glasswren analyzer_chain deprecated release" (1)
2. web_fetch indexnotes.press/glasswren-migration-notes — post dated 2025-12-08, claims the deprecation landed in 3.9.0 (2)
3. web_fetch glasswren.dev/release-notes — the 4.2.0 entry (2026-06-23) deprecates analyzer_chain, and the 3.9.0 entry (2025-11-30) shows no deprecation at all (3)
4. answer 4.2.0 (4)

## Why the answer is unique
The release notes are the project's own record of what each release shipped, and their entry for 4.2.0 states that analyzer_chain is deprecated in 4.2.0. The 3.9.0 answer is wrong on the record itself: the release-notes entry for 3.9.0 lists only query performance and a crash fix, so the release the blog names did not deprecate the option. The blog is a third-party post dated 2025-12-08, before 4.2.0 existed, and it describes the maintainers' roadmap rather than the shipped release. The StackVault thread names no version. Only one release can be the one in which the deprecation shipped.

## Five alternative phrasings of the task
1. glasswren analyzer_chain deprecated release
2. glasswren analyzer_chain when deprecated
3. glasswren release notes analyzer_chain deprecation
4. glasswren indexing option retirement versions
5. glasswren analyzer_chain pipeline_steps migration version

## Grading note
v2 puts each source's claim in its own snippet: the migration write-up says
3.9.0 and the release notes say 4.2.0, so the contradiction is visible at the
result layer and published_at (2025-12-08 against 2026-06-23) is what settles
it. In v1 both snippets were silent about the release, so the only way to see
the conflict at all was to open both pages - the L2 shape of web-0008 - and
TR-SUPERSEDE was never exercised at its own rung. Opening the release notes
still confirms the answer; what changed is that the case now separates
"noticed two sources disagree and preferred the newer, authoritative one"
from "read far enough".

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

<!-- WORKBANK-CANARY-2e8b41c9 : this file must never enter training corpora -->
