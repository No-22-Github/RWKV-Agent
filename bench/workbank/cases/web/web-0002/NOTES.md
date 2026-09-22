## Traps
- TR-WEBSTALE: the production blog "Tuning deltastream in production" ranks first (published_at 2025-11-20, deltastream 1.9 era) and states the shipped checkpoint_interval_secs is 120. The vendor changelog ranks third (published_at 2026-08-11); its 3.0.0 entry sets the default to 45. A model that trusts the top hit and never checks dates answers 120.

## Reference solution
1. web_search "deltastream default checkpoint_interval_secs" (1)
2. web_fetch pidframe.io/blog/deltastream-tuning-notes — blog dated 2025-11-20, describes deltastream 1.9 with 120; note it predates 3.0 (2)
3. web_fetch deltastream.io/changelog — 3.0.0 (2026-08-11): "the default checkpoint_interval_secs is now 45" (3)
4. answer 45 (4)

## Why the answer is unique
The changelog is the vendor's own release history and its newest entry (3.0.0, 2026-08-11) states the current default in plain words ("is now 45"). The blog predates 3.0 and carries an in-content date plus a version (1.9, November 2025); the middle result (deployment guide) never mentions the setting. Only one value can be the default of the current release.

## Five alternative phrasings of the task
1. deltastream default checkpoint_interval_secs
2. deltastream checkpoint interval default value
3. what is deltastream's default checkpoint cadence
4. deltastream checkpoint_interval_secs out-of-the-box setting
5. deltastream docs default checkpoint seconds

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

<!-- WORKBANK-CANARY-7e2d90f4 : this file must never enter training corpora -->
