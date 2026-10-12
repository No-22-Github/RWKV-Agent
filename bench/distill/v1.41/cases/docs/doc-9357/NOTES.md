## Traps
- TR-MULTISRC: the dead links are spread over seven pages and one page can hold two of them; every occurrence counts. 改名表.txt is data, not a page. Turn 3 only works on 附录.md and FAQ.md, whose links to renamed targets were all dead originally.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep -ho '([^()]*\.md)' 知识库/*.md | tr -d '()' | while read t; do [ -e 知识库/$t ] || echo $t; done | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/(安装指南.md)/(安装.md)/g' 知识库/*.md; sed -i 's/(常见问题.md)/(FAQ.md)/g' 知识库/*.md; sed -i 's/(快速入门.md)/(入门.md)/g' 知识库/*.md`
2. bash: `grep -rn '](' 知识库`
Turn 3 (edit, reply DONE):
1. bash: `sed -i 's/(安装.md)/(安装指南.md)/g' 知识库/附录.md 知识库/FAQ.md; sed -i 's/(FAQ.md)/(常见问题.md)/g' 知识库/附录.md 知识库/FAQ.md; sed -i 's/(入门.md)/(快速入门.md)/g' 知识库/附录.md 知识库/FAQ.md`
2. bash: `grep -n '](' 知识库/附录.md 知识库/FAQ.md`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 知识库里有几个链接已经失效？按改名表修好，之后附录和 FAQ 两页再改回旧名
2. 数一下指向不存在文件的链接，用改名表替换成新文件名，然后让附录.md 和 FAQ.md 恢复原状
3. 统计知识库里的失效链接，对照改名表批量更新，最后把附录与 FAQ 的改动撤销
4. 失效链接有多少个？修复它们，但附录.md 和 FAQ.md 要保留旧链接
5. How many links in 知识库 point to files that no longer exist? Fix them with the rename table, then put the old names back in 附录.md and FAQ.md.
