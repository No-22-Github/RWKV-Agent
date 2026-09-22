## Traps
- None planted (L0 base case). The three fixture pages agree with each other: the vendor deprecations page ranks first and its retired-options table carries the release, and the blog and the forum thread both point back at that page without naming a different release. No page states a competing version, so there is no bait to fall for.

## Reference solution
1. web_search "cindermill remote_verify deprecated release" (1)
2. web_fetch docs.cindermill.io/reference/deprecations — the retired-options table lists remote_verify with "Deprecated in" 2.7.0 (2)
3. answer 2.7.0 (3)

## Why the answer is unique
The deprecations page is the vendor's own reference and its retired-options table gives exactly one release for remote_verify, 2.7.0. The two other fixture pages carry no version at all: the engineering blog describes the config change and defers to the deprecations page, and the forum thread answers "is it going away" by pointing at the same page. No fixture entry puts a second release against this option, so there is nothing to weigh against 2.7.0.

## Five alternative phrasings of the task
1. cindermill remote_verify deprecation release
2. cindermill when was remote_verify deprecated
3. cindermill docs deprecated options remote_verify
4. cindermill option removal versions
5. cindermill remote_verify replaced by verify_mode version

## Grading note
v2 lifts the answer into the first result's snippet. As the L0 rung of this
family the case is meant to be answerable from the result layer; v1's three
snippets all stopped short of the release number, so the case silently
carried web-0007's L1 increment ("the summary says the option moved, the
release is only in the page"). The page still has to be opened to check the
table, but a solver that answers from the result layer is now right rather
than lucky. The prompt's framing sentence also said "removal timeline",
which pulled against the page's own removal-is-not-deprecation wording; it
now says deprecation release, which is what the question and the expectation
ask for.

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

<!-- WORKBANK-CANARY-6c1f0a7d : this file must never enter training corpora -->
