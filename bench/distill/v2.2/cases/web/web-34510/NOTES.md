## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
作答。
第二轮追问同一页面的细节：search_text 在 .web 里搜或 read_file 跳读，再作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
12402
(fixture: fenwick-energy.example/customers/tariff-guide-2027=5952)


## Five alternative phrasings of the task
1. Can you go through https://fenwick-energy.example/customers/tariff-guide-2027 and tell me what the 2027 tariffs look like, including the Flex Saver and Green Fix options?
2. 麻烦帮我：Can you go through https://fenwick-energy.example/customers/tariff-guide-2027 and tell me what the 2027 tariffs look like, including the Flex Saver and Green Fix options?
3. Can you go through https://fenwick-energy.example/customers/tariff-guide-2027 and tell me what the 2027 tariffs look like, including the Flex Saver and Green Fix options? (keep it organised)
4. 想请你看看：Can you go through https://fenwick-energy.example/customers/tariff-guide-2027 and tell me what the 2027 tariffs look like, including the Flex Saver and Green Fix options?
5. 再确认一下：Can you go through https://fenwick-energy.example/customers/tariff-guide-2027 and tell me what the 2027 tariffs look like, including the Flex Saver and Green Fix options?
