## Traps
TR-TRUNC

## Reference solution
web_search -> web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
write_file 写入 subsidy-guide.md
作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
9595
(fixture: yunqi-hr.example/policy/talent-subsidy-2026=5745)


## Five alternative phrasings of the task
1. 我想了解云栖市人才安居补贴怎么申请，帮我找一下人社局的指南，把条件、金额、材料和时间整理到 subsidy-guide.md 里。
2. 麻烦帮我：我想了解云栖市人才安居补贴怎么申请，帮我找一下人社局的指南，把条件、金额、材料和时间整理到 subsidy-guide.md 里。
3. 我想了解云栖市人才安居补贴怎么申请，帮我找一下人社局的指南，把条件、金额、材料和时间整理到 subsidy-guide.md 里。（用中文回答）
4. 想请你看看：我想了解云栖市人才安居补贴怎么申请，帮我找一下人社局的指南，把条件、金额、材料和时间整理到 subsidy-guide.md 里。
5. 再确认一下：我想了解云栖市人才安居补贴怎么申请，帮我找一下人社局的指南，把条件、金额、材料和时间整理到 subsidy-guide.md 里。
