## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
13733
(fixture: nimbusapi.example/blog/api-v1-deprecation-timeline=5788, nimbusapi.example/docs/v1-sunset-faq=3845)


## Five alternative phrasings of the task
1. Our integration still uses Nimbus API v1. Read https://nimbusapi.example/blog/api-v1-deprecation-timeline and the FAQ it links to, then summarise the dates, limits and changes I must plan for.
2. 麻烦帮我：Our integration still uses Nimbus API v1. Read https://nimbusapi.example/blog/api-v1-deprecation-timeline and the FAQ it links to, then summarise the dates, limits and changes I must plan for.
3. Our integration still uses Nimbus API v1. Read https://nimbusapi.example/blog/api-v1-deprecation-timeline and the FAQ it links to, then summarise the dates, limits and changes I must plan for. (keep it organised)
4. 想请你看看：Our integration still uses Nimbus API v1. Read https://nimbusapi.example/blog/api-v1-deprecation-timeline and the FAQ it links to, then summarise the dates, limits and changes I must plan for.
5. 再确认一下：Our integration still uses Nimbus API v1. Read https://nimbusapi.example/blog/api-v1-deprecation-timeline and the FAQ it links to, then summarise the dates, limits and changes I must plan for.
