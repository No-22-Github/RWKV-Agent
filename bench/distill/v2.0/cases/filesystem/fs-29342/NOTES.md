## Traps
- TR-DECOY: 素材/归档/旧封面.png is bigger than everything else but archived (素材/README.md). The move has two ends: the picture and its same-named .meta file, nothing else moves.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `wc -c 素材/*.* | sort -rn | head -4`
Turn 2 (edit, reply DONE):
1. bash: `mv 素材/封面.png 素材/封面.png.meta 素材/归档/`
2. bash: `ls 素材 素材/归档`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 素材里最大的图片是哪张？找到后和它的 .meta 一起归档
2. 不算归档，最大的 png 叫什么？把它和说明文件放进归档目录
3. 找出素材目录体积最大的那个 png，再把它与 .meta 都挪进归档
4. 素材库里哪个图片文件最大（归档除外）？归档它和对应的说明文件
5. Which .png in 素材 is the biggest (not counting 归档)? Move it and its .meta file into 素材/归档.
