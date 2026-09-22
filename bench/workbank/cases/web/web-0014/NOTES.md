## Traps
- TR-EARLYHIT: the first search result (threadneedle.io/releases) has a snippet that states the current stable release outright, 7.4.1, so one search is enough to answer. The case-level `expect.max_calls` of `{"web_search": 1}` fails a trace that issues a second search: the extra query is scored as redundant, whether or not it is rejected as a duplicate. A model that keeps searching and lands on the 7.3-era write-up reports 7.3.0.

## Reference solution
1. web_search "threadneedle newest stable release" (1) — the first result's snippet reads "The current stable threadneedle release is 7.4.1, published 2026-08-19."
2. answer 7.4.1 (2)

## Why the answer is unique
The releases page lists tagged releases newest first and its own summary line names 7.4.1 as the current stable release, dated 2026-08-19. The other entries cannot compete: the operations write-up is dated 2025-12-02 and pinned the 7.3 line a year earlier, and the repository README carries no version at all. Only one release can be the newest, and only one fixture entry asserts which one it is.

## Five alternative phrasings of the task
1. threadneedle newest stable release
2. threadneedle current release version
3. what version of threadneedle is current
4. threadneedle releases page current tag
5. threadneedle latest tagged release

## Grading note
v1 graded with `output_equals: "7.4.1"`. Answer normalization lowercases and
strips emphasis and trailing punctuation but nothing else, so the reply
"7.4.1 (2026-08-19)" - the release with the date the page prints beside it -
was scored wrong. v2 uses `output_equals_any` and accepts both forms.

It stops there rather than moving to a substring check, which would tolerate
any wording. This case has no workspace files, so verify_all skips the
sabotage test on it, and matching verify.py's extracted string against the
`output_equals` family is the only automated tie between the expectation and
the fixture it came from. A substring expectation is invisible to that check
(verify_all collects `output_equals` / `output_equals_any` / `expected_number`
only), and the case would be left with no cross-check at all. Wider tolerance
is worth having, and it is filed with the S-C tools item: once verify_all
collects `output_contains`, this can become a contains-check.

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

<!-- WORKBANK-CANARY-2f8a6d05 : this file must never enter training corpora -->
