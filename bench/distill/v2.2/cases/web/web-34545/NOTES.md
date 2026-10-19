## Traps
TR-TRUNC, TR-SUPERSEDE

## Reference solution
 一次 web_fetch 同时取 3 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
15133
(fixture: stdcentral.example/standards/sec-7000/2025=3796, stdcentral.example/standards/sec-7000/2020=3684, secnotes-blog.example/posts/sec-7000-whats-new=3303)


## Five alternative phrasings of the task
1. I'm preparing for an ISO-style audit under SEC-7000. Read https://stdcentral.example/standards/sec-7000/2025 , https://stdcentral.example/standards/sec-7000/2020 and the blog summary https://secnotes-blog.example/posts/sec-7000-whats-new . Which edition is current, what changed in controls and incident reporting, and what is the transition deadline?
2. 麻烦帮我：I'm preparing for an ISO-style audit under SEC-7000. Read https://stdcentral.example/standards/sec-7000/2025 , https://stdcentral.example/standards/sec-7000/2020 and the blog summary https://secnotes-blog.example/posts/sec-7000-whats-new . Which edition is current, what changed in controls and incident reporting, and what is the transition deadline?
3. I'm preparing for an ISO-style audit under SEC-7000. Read https://stdcentral.example/standards/sec-7000/2025 , https://stdcentral.example/standards/sec-7000/2020 and the blog summary https://secnotes-blog.example/posts/sec-7000-whats-new . Which edition is current, what changed in controls and incident reporting, and what is the transition deadline? (keep it organised)
4. 想请你看看：I'm preparing for an ISO-style audit under SEC-7000. Read https://stdcentral.example/standards/sec-7000/2025 , https://stdcentral.example/standards/sec-7000/2020 and the blog summary https://secnotes-blog.example/posts/sec-7000-whats-new . Which edition is current, what changed in controls and incident reporting, and what is the transition deadline?
5. 再确认一下：I'm preparing for an ISO-style audit under SEC-7000. Read https://stdcentral.example/standards/sec-7000/2025 , https://stdcentral.example/standards/sec-7000/2020 and the blog summary https://secnotes-blog.example/posts/sec-7000-whats-new . Which edition is current, what changed in controls and incident reporting, and what is the transition deadline?
