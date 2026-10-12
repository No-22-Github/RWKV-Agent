## Traps
- TR-DECOY: one page has the comment on line 3 (not the first line, so it counts), others use another group's comment (counts as present). TR-READONLY: README.md and 手册/_第三方 are not ours (手册/README.md).
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in $(find 手册 -name '*.md' | grep -v _第三方 | grep -v README.md); do head -1 $f | grep -q '^<!-- owner' || echo $f; done | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `for f in $(find 手册 -name '*.md' | grep -v _第三方 | grep -v README.md); do head -1 $f | grep -q '^<!-- owner' || sed -i '1i <!-- owner: docs-team -->' $f; done`
2. bash: `head -n 2 手册/*.md 手册/附录/*.md`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 手册里有几页没有在第一行写 owner 注释？给它们补上 docs-team 的注释
2. 统计第一行不是 owner 注释的页面数，然后在这些页面顶部插入那条注释
3. 手册页面中缺 owner 注释的有多少个？把它们的首行补齐
4. 数一数手册里首行缺 owner 注释的页面，再给这些页面加上「<!-- owner: docs-team -->」
5. How many manual pages lack the owner comment on line 1? Add the docs-team comment to each.
