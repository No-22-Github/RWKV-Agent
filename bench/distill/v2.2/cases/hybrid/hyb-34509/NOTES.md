## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 visit-rules.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
10146
(fixture: haitang-hospital.example/service/visiting-rules=6296)


## Five alternative phrasings of the task
1. 帮我整理一份海棠医院的探视和陪护规定摘要，原文在 https://haitang-hospital.example/service/visiting-rules ，我要发给家里人，请写到 visit-rules.md 里，包括普通病区、重症监护和感染科的区别。
2. 麻烦帮我：帮我整理一份海棠医院的探视和陪护规定摘要，原文在 https://haitang-hospital.example/service/visiting-rules ，我要发给家里人，请写到 visit-rules.md 里，包括普通病区、重症监护和感染科的区别。
3. 帮我整理一份海棠医院的探视和陪护规定摘要，原文在 https://haitang-hospital.example/service/visiting-rules ，我要发给家里人，请写到 visit-rules.md 里，包括普通病区、重症监护和感染科的区别。（用中文回答）
4. 想请你看看：帮我整理一份海棠医院的探视和陪护规定摘要，原文在 https://haitang-hospital.example/service/visiting-rules ，我要发给家里人，请写到 visit-rules.md 里，包括普通病区、重症监护和感染科的区别。
5. 再确认一下：帮我整理一份海棠医院的探视和陪护规定摘要，原文在 https://haitang-hospital.example/service/visiting-rules ，我要发给家里人，请写到 visit-rules.md 里，包括普通病区、重症监护和感染科的区别。
