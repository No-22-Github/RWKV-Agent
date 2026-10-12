## Traps
- TR-MULTISRC: four monthly files, every one has its own header line. Negative amounts are returns and count in the total (汇总/README.md). TR-READONLY: 汇总/2025年.csv is last year's file and stays.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `cat 订单/*.csv | grep -v '^品类' | awk -F, '{s[$1]+=$2} END{for(k in s) print k","s[k]}' | sort -t, -k2 -nr`
Turn 2 (edit, reply DONE):
1. bash: `for c in 数码 日用 生鲜 零食 饮料; do (echo '品类,金额'; cat 订单/*.csv | grep "^$c,") > 汇总/$c.csv; done && echo '最大品类：日用' > 汇总/结论.txt`
2. bash: `ls 汇总; cat 汇总/结论.txt`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 四个月订单按品类汇总，谁最大？再把每个品类的行拆成单独文件并写结论
2. 统计 7 到 10 月各品类金额（负数计入），找出最大的，然后按品类生成 csv 和结论.txt
3. 哪个品类四个月加起来最多？按 README 的格式拆分出各品类文件并写结论文件
4. 把订单目录的四个月数据按品类求和，最大品类回答出来，并把各品类的行分别写入汇总里的文件
5. Which category has the largest total over the four monthly order files (negatives count)? Then split the rows into one CSV per category in 汇总 and write 结论.txt.
