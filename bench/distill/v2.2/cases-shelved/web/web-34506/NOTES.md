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
12606
(fixture: mingli-univ.example/registrar/rules/course-selection=6156)


## Five alternative phrasings of the task
1. 我是明理大学的新生，想弄清选课规则。这是教务处的办法 https://mingli-univ.example/registrar/rules/course-selection ，帮我整理一份要点，重点是学分上限、退课时间、补考和辅修条件。
2. 麻烦帮我：我是明理大学的新生，想弄清选课规则。这是教务处的办法 https://mingli-univ.example/registrar/rules/course-selection ，帮我整理一份要点，重点是学分上限、退课时间、补考和辅修条件。
3. 我是明理大学的新生，想弄清选课规则。这是教务处的办法 https://mingli-univ.example/registrar/rules/course-selection ，帮我整理一份要点，重点是学分上限、退课时间、补考和辅修条件。（用中文回答）
4. 想请你看看：我是明理大学的新生，想弄清选课规则。这是教务处的办法 https://mingli-univ.example/registrar/rules/course-selection ，帮我整理一份要点，重点是学分上限、退课时间、补考和辅修条件。
5. 再确认一下：我是明理大学的新生，想弄清选课规则。这是教务处的办法 https://mingli-univ.example/registrar/rules/course-selection ，帮我整理一份要点，重点是学分上限、退课时间、补考和辅修条件。
