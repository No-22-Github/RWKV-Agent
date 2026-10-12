## Traps
- TR-DECOY: names do not tell: copies have new names, and 副本/IMG_101.jpg shares a name with an original but has different content; retouched versions differ by one line. TR-READONLY: 原始 stays untouched (照片/README.md).
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in 照片/副本/*; do h=$(md5sum $f | cut -d" " -f1); md5sum 照片/原始/* | grep -q "^$h" && echo $f; done | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `for f in 照片/副本/*; do h=$(md5sum $f | cut -d" " -f1); md5sum 照片/原始/* | grep -q "^$h" && rm $f; done`
2. bash: `ls 照片/副本`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 副本目录里有多少文件是原始文件的逐字拷贝？把它们删除
2. 统计内容与原始完全一致的副本个数，然后删掉这些副本，修图版本留着
3. 照片/副本 中有几个文件和原始里的某个文件内容一样？删去这些，其余不动
4. 按内容比对副本和原始，数出重复的副本并清理掉
5. How many files in 照片/副本 are byte-identical to some file in 照片/原始? Delete exactly those copies.
