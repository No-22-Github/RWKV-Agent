## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14290
(fixture: north-univ.example/admission/master-2027=5150, southgate-univ.example/yz/2027-zhaosheng=4990)


## Five alternative phrasings of the task
1. 我在北辰大学和南门大学之间选计算机硕士。两份简章：https://north-univ.example/admission/master-2027 、https://southgate-univ.example/yz/2027-zhaosheng 。帮我比较招生人数、学制、复试占比和奖学金，各自哪个更划算。
2. 麻烦帮我：我在北辰大学和南门大学之间选计算机硕士。两份简章：https://north-univ.example/admission/master-2027 、https://southgate-univ.example/yz/2027-zhaosheng 。帮我比较招生人数、学制、复试占比和奖学金，各自哪个更划算。
3. 我在北辰大学和南门大学之间选计算机硕士。两份简章：https://north-univ.example/admission/master-2027 、https://southgate-univ.example/yz/2027-zhaosheng 。帮我比较招生人数、学制、复试占比和奖学金，各自哪个更划算。（用中文回答）
4. 想请你看看：我在北辰大学和南门大学之间选计算机硕士。两份简章：https://north-univ.example/admission/master-2027 、https://southgate-univ.example/yz/2027-zhaosheng 。帮我比较招生人数、学制、复试占比和奖学金，各自哪个更划算。
5. 再确认一下：我在北辰大学和南门大学之间选计算机硕士。两份简章：https://north-univ.example/admission/master-2027 、https://southgate-univ.example/yz/2027-zhaosheng 。帮我比较招生人数、学制、复试占比和奖学金，各自哪个更划算。
