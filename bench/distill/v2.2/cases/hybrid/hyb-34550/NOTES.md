## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 sla-comparison.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14534
(fixture: vaultbox.example/legal/sla=5050, stowaway.example/sla=5084)


## Five alternative phrasings of the task
1. Our legal team wants a quick SLA comparison. Read https://vaultbox.example/legal/sla and https://stowaway.example/sla and write sla-comparison.md with uptime commitments, credit tiers, durability and exclusions for each.
2. 麻烦帮我：Our legal team wants a quick SLA comparison. Read https://vaultbox.example/legal/sla and https://stowaway.example/sla and write sla-comparison.md with uptime commitments, credit tiers, durability and exclusions for each.
3. Our legal team wants a quick SLA comparison. Read https://vaultbox.example/legal/sla and https://stowaway.example/sla and write sla-comparison.md with uptime commitments, credit tiers, durability and exclusions for each. (keep it organised)
4. 想请你看看：Our legal team wants a quick SLA comparison. Read https://vaultbox.example/legal/sla and https://stowaway.example/sla and write sla-comparison.md with uptime commitments, credit tiers, durability and exclusions for each.
5. 再确认一下：Our legal team wants a quick SLA comparison. Read https://vaultbox.example/legal/sla and https://stowaway.example/sla and write sla-comparison.md with uptime commitments, credit tiers, durability and exclusions for each.
