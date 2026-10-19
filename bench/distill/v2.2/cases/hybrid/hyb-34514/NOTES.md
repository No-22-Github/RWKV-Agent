## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 advisory-brief.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
9559
(fixture: vantor-sys.example/security/advisories/adv-2026-014=5709)


## Five alternative phrasings of the task
1. Make an internal briefing in advisory-brief.md from https://vantor-sys.example/security/advisories/adv-2026-014 : who is affected, what to do before patching and which versions fix it.
2. 麻烦帮我：Make an internal briefing in advisory-brief.md from https://vantor-sys.example/security/advisories/adv-2026-014 : who is affected, what to do before patching and which versions fix it.
3. Make an internal briefing in advisory-brief.md from https://vantor-sys.example/security/advisories/adv-2026-014 : who is affected, what to do before patching and which versions fix it. (keep it organised)
4. 想请你看看：Make an internal briefing in advisory-brief.md from https://vantor-sys.example/security/advisories/adv-2026-014 : who is affected, what to do before patching and which versions fix it.
5. 再确认一下：Make an internal briefing in advisory-brief.md from https://vantor-sys.example/security/advisories/adv-2026-014 : who is affected, what to do before patching and which versions fix it.
