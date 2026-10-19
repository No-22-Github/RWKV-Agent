## Traps
- TR-WEBSTALE
- 对照组：题面指的是『我们项目里/这份文件里的』值；上网拿到的是另一个数。

## Reference solution
list_files/search_text 找到文件 -> read_file 读出 -> 直接作答（不上网）；第二轮追问外部信息再 web_search

## Why the answer is unique
The user's own file states the value; the web fixture deliberately carries a different one.

Expected: 300 | 360

## Five alternative phrasings of the task
1. 我们物业公告里写的樱桃停车场月租多少钱？
2. 想确认一下：我们物业公告里写的樱桃停车场月租多少钱？
3. 我们物业公告里写的樱桃停车场月租多少钱？（简单说就行）
4. 麻烦帮我看看：我们物业公告里写的樱桃停车场月租多少钱？
5. 再问一件事：我们物业公告里写的樱桃停车场月租多少钱？
