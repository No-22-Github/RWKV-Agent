## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 helpdesk-compare.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14825
(fixture: brightdesk.example/pricing=5279, deskhub.example/plans=5146)


## Five alternative phrasings of the task
1. Compare the two helpdesk tools for me using https://brightdesk.example/pricing and https://deskhub.example/plans . Write helpdesk-compare.md with prices, automation limits, ticket history and trial terms for each, and say which page is more recent.
2. 麻烦帮我：Compare the two helpdesk tools for me using https://brightdesk.example/pricing and https://deskhub.example/plans . Write helpdesk-compare.md with prices, automation limits, ticket history and trial terms for each, and say which page is more recent.
3. Compare the two helpdesk tools for me using https://brightdesk.example/pricing and https://deskhub.example/plans . Write helpdesk-compare.md with prices, automation limits, ticket history and trial terms for each, and say which page is more recent. (keep it organised)
4. 想请你看看：Compare the two helpdesk tools for me using https://brightdesk.example/pricing and https://deskhub.example/plans . Write helpdesk-compare.md with prices, automation limits, ticket history and trial terms for each, and say which page is more recent.
5. 再确认一下：Compare the two helpdesk tools for me using https://brightdesk.example/pricing and https://deskhub.example/plans . Write helpdesk-compare.md with prices, automation limits, ticket history and trial terms for each, and say which page is more recent.
