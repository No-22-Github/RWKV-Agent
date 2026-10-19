## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 3 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
15446
(fixture: shuguang-pay.example/status/incident-1017=4325, tech-daily.example/news/shuguang-pay-outage=3430, regulator-fin.example/notice/payment-outage-1019=3341)


## Five alternative phrasings of the task
1. 曙光支付 10 月 17 日出了故障。公司报告 https://shuguang-pay.example/status/incident-1017 、新闻快讯 https://tech-daily.example/news/shuguang-pay-outage 、监管通报 https://regulator-fin.example/notice/payment-outage-1019 ，请汇总：故障到底持续多久、影响面、根因、监管要求，并说明新闻里的数字哪些和公司报告不一致。
2. 麻烦帮我：曙光支付 10 月 17 日出了故障。公司报告 https://shuguang-pay.example/status/incident-1017 、新闻快讯 https://tech-daily.example/news/shuguang-pay-outage 、监管通报 https://regulator-fin.example/notice/payment-outage-1019 ，请汇总：故障到底持续多久、影响面、根因、监管要求，并说明新闻里的数字哪些和公司报告不一致。
3. 曙光支付 10 月 17 日出了故障。公司报告 https://shuguang-pay.example/status/incident-1017 、新闻快讯 https://tech-daily.example/news/shuguang-pay-outage 、监管通报 https://regulator-fin.example/notice/payment-outage-1019 ，请汇总：故障到底持续多久、影响面、根因、监管要求，并说明新闻里的数字哪些和公司报告不一致。（用中文回答）
4. 想请你看看：曙光支付 10 月 17 日出了故障。公司报告 https://shuguang-pay.example/status/incident-1017 、新闻快讯 https://tech-daily.example/news/shuguang-pay-outage 、监管通报 https://regulator-fin.example/notice/payment-outage-1019 ，请汇总：故障到底持续多久、影响面、根因、监管要求，并说明新闻里的数字哪些和公司报告不一致。
5. 再确认一下：曙光支付 10 月 17 日出了故障。公司报告 https://shuguang-pay.example/status/incident-1017 、新闻快讯 https://tech-daily.example/news/shuguang-pay-outage 、监管通报 https://regulator-fin.example/notice/payment-outage-1019 ，请汇总：故障到底持续多久、影响面、根因、监管要求，并说明新闻里的数字哪些和公司报告不一致。
