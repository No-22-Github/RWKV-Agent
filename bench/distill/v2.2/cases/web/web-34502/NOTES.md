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
12567
(fixture: quillmark.example/docs/releases/4-0=6117)


## Five alternative phrasings of the task
1. Please read https://quillmark.example/docs/releases/4-0 and write me a summary of what changes in 4.0 and what I need to do before upgrading.
2. 麻烦帮我：Please read https://quillmark.example/docs/releases/4-0 and write me a summary of what changes in 4.0 and what I need to do before upgrading.
3. Please read https://quillmark.example/docs/releases/4-0 and write me a summary of what changes in 4.0 and what I need to do before upgrading. (keep it organised)
4. 想请你看看：Please read https://quillmark.example/docs/releases/4-0 and write me a summary of what changes in 4.0 and what I need to do before upgrading.
5. 再确认一下：Please read https://quillmark.example/docs/releases/4-0 and write me a summary of what changes in 4.0 and what I need to do before upgrading.
