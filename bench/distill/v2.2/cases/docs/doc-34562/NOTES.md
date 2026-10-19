## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（support/emea-escalations.md 634 行、support/apac-escalations.md 732 行、support/americas-escalations.md 844 行、support/partner-escalations.md 466 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态和负责人
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 lena-escalated-waiting.md，列出 8 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open and the named owner; decoys differ in exactly one field.

## Estimated trajectory tokens
12490
(fixture: support/emea-escalations.md=5013, support/apac-escalations.md=5897, support/americas-escalations.md=6848, support/partner-escalations.md=3701)
lines per document: [634, 732, 844, 466]

## Five alternative phrasings of the task
1. Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md.
2. 麻烦帮我：Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md.
3. Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md. (keep it organised)
4. 想请你看看：Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md.
5. 再确认一下：Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md.
