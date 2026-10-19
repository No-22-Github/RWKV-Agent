## Traps
- TR-ABSENT
- 题面已说明本地没有资料；碰本地工具（list_files/search_text/read_file）即判错。

## Reference solution
第一步直接 web_search -> 作答；追问再查网页

## Why the answer is unique
Prompt says the workspace has no such material; the value is in the web fixture only.

Expected: 0.88.1 | plugin

## Five alternative phrasings of the task
1. Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.
2. 想确认一下：Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.
3. Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.（简单说就行）
4. 麻烦帮我看看：Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.
5. 再问一件事：Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.
