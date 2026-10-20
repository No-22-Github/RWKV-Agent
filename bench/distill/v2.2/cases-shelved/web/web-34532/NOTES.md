## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 3 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
15490
(fixture: stratus-host.example/pricing=3907, cloudcompare-weekly.example/hosting/stratus-vs-rivals=4036, hostingtalk-forum.example/t/stratus-price-hike=3197)


## Five alternative phrasings of the task
1. I'm comparing what Stratus Host costs now. Check the official page https://stratus-host.example/pricing, the review https://cloudcompare-weekly.example/hosting/stratus-vs-rivals and the forum thread https://hostingtalk-forum.example/t/stratus-price-hike . Which one is the most current and official, and what are the actual prices, bandwidth allowance and the grace period for existing customers?
2. 麻烦帮我：I'm comparing what Stratus Host costs now. Check the official page https://stratus-host.example/pricing, the review https://cloudcompare-weekly.example/hosting/stratus-vs-rivals and the forum thread https://hostingtalk-forum.example/t/stratus-price-hike . Which one is the most current and official, and what are the actual prices, bandwidth allowance and the grace period for existing customers?
3. I'm comparing what Stratus Host costs now. Check the official page https://stratus-host.example/pricing, the review https://cloudcompare-weekly.example/hosting/stratus-vs-rivals and the forum thread https://hostingtalk-forum.example/t/stratus-price-hike . Which one is the most current and official, and what are the actual prices, bandwidth allowance and the grace period for existing customers? (keep it organised)
4. 想请你看看：I'm comparing what Stratus Host costs now. Check the official page https://stratus-host.example/pricing, the review https://cloudcompare-weekly.example/hosting/stratus-vs-rivals and the forum thread https://hostingtalk-forum.example/t/stratus-price-hike . Which one is the most current and official, and what are the actual prices, bandwidth allowance and the grace period for existing customers?
5. 再确认一下：I'm comparing what Stratus Host costs now. Check the official page https://stratus-host.example/pricing, the review https://cloudcompare-weekly.example/hosting/stratus-vs-rivals and the forum thread https://hostingtalk-forum.example/t/stratus-price-hike . Which one is the most current and official, and what are the actual prices, bandwidth allowance and the grace period for existing customers?
