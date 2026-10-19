## Traps
TR-TRUNC, TR-SUPERSEDE

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
13249
(fixture: dataguard-agency.example/guidance/retention-2026=5308, lawfirm-ashdown.example/insights/retention-explained=3791)


## Five alternative phrasings of the task
1. A client asks what the new retention rules are. Read the regulator's text https://dataguard-agency.example/guidance/retention-2026 and the law firm briefing https://lawfirm-ashdown.example/insights/retention-explained , and tell me which figures are current, which are from the draft, and what differs.
2. 麻烦帮我：A client asks what the new retention rules are. Read the regulator's text https://dataguard-agency.example/guidance/retention-2026 and the law firm briefing https://lawfirm-ashdown.example/insights/retention-explained , and tell me which figures are current, which are from the draft, and what differs.
3. A client asks what the new retention rules are. Read the regulator's text https://dataguard-agency.example/guidance/retention-2026 and the law firm briefing https://lawfirm-ashdown.example/insights/retention-explained , and tell me which figures are current, which are from the draft, and what differs. (keep it organised)
4. 想请你看看：A client asks what the new retention rules are. Read the regulator's text https://dataguard-agency.example/guidance/retention-2026 and the law firm briefing https://lawfirm-ashdown.example/insights/retention-explained , and tell me which figures are current, which are from the draft, and what differs.
5. 再确认一下：A client asks what the new retention rules are. Read the regulator's text https://dataguard-agency.example/guidance/retention-2026 and the law firm briefing https://lawfirm-ashdown.example/insights/retention-explained , and tell me which figures are current, which are from the draft, and what differs.
