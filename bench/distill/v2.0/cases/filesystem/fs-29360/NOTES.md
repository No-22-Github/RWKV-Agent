## Traps
- TR-DECOY: 旧报告.pdf.bak and 旧合同.pdf.bak have extension bak (下载/README.md), so they neither count as pdf nor move. Turn 3 moves exactly the keep_* files back; all other pdf files stay in the subfolder.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `ls 下载 | grep '\.' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -3`
Turn 2 (edit, reply DONE):
1. bash: `mv 下载/*.pdf 下载/pdf/`
2. bash: `ls 下载 下载/pdf`
Turn 3 (edit, reply DONE):
1. bash: `mv 下载/pdf/keep_*.pdf 下载/`
2. bash: `ls 下载 下载/pdf`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 下载里哪种扩展名的文件最多？把它们归到同名子目录，再把 keep_ 开头的搬回根目录
2. 找出数量最多的扩展名，整理进 下载/<扩展名>，keep_ 前缀的文件之后放回原处
3. 按扩展名统计下载目录，最多的那类移进子目录，然后把 keep_ 开头的移回来
4. 最常见的文件类型是什么？把这类文件收进子目录（keep_ 开头的除外，需要再移回）
5. Which extension is most common in 下载? Move those files into a subfolder named after it, then move the keep_ ones back.
