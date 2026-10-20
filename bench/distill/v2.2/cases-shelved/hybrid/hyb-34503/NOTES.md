## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 bike-rule-summary.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
10119
(fixture: qinghe-city.example/gov/notice/2026-bike-rule=6269)


## Five alternative phrasings of the task
1. 青禾市交通局有一份共享单车管理通知（https://qinghe-city.example/gov/notice/2026-bike-rule），帮我整理成给运营公司同事看的要点，写到 bike-rule-summary.md 里。
2. 麻烦帮我：青禾市交通局有一份共享单车管理通知（https://qinghe-city.example/gov/notice/2026-bike-rule），帮我整理成给运营公司同事看的要点，写到 bike-rule-summary.md 里。
3. 青禾市交通局有一份共享单车管理通知（https://qinghe-city.example/gov/notice/2026-bike-rule），帮我整理成给运营公司同事看的要点，写到 bike-rule-summary.md 里。（用中文回答）
4. 想请你看看：青禾市交通局有一份共享单车管理通知（https://qinghe-city.example/gov/notice/2026-bike-rule），帮我整理成给运营公司同事看的要点，写到 bike-rule-summary.md 里。
5. 再确认一下：青禾市交通局有一份共享单车管理通知（https://qinghe-city.example/gov/notice/2026-bike-rule），帮我整理成给运营公司同事看的要点，写到 bike-rule-summary.md 里。
