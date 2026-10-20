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
12777
(fixture: xinghe-reader.example/review/x7-long-term=6327)


## Five alternative phrasings of the task
1. 我在考虑买星河 X7 电子阅读器，网上有篇长评（https://xinghe-reader.example/review/x7-long-term），帮我总结一下优缺点，并写明续航和价格。
2. 麻烦帮我：我在考虑买星河 X7 电子阅读器，网上有篇长评（https://xinghe-reader.example/review/x7-long-term），帮我总结一下优缺点，并写明续航和价格。
3. 我在考虑买星河 X7 电子阅读器，网上有篇长评（https://xinghe-reader.example/review/x7-long-term），帮我总结一下优缺点，并写明续航和价格。（用中文回答）
4. 想请你看看：我在考虑买星河 X7 电子阅读器，网上有篇长评（https://xinghe-reader.example/review/x7-long-term），帮我总结一下优缺点，并写明续航和价格。
5. 再确认一下：我在考虑买星河 X7 电子阅读器，网上有篇长评（https://xinghe-reader.example/review/x7-long-term），帮我总结一下优缺点，并写明续航和价格。
