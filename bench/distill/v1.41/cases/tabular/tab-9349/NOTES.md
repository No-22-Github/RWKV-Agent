## Traps
- TR-DECOY: A-1000 and A-100X are different part numbers that start with A-100 (a prefix grep returns them too). TR-READONLY: other part numbers and each day's order quantity stay (采购/README.md).
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep '^A-100,' 报价/*.csv`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/^A-100,.*$/A-100,远航/' 采购/默认供应商.csv && sed -i 's/^A-100,[^,]*,[^,]*,/A-100,远航,45,/' 采购/下单/*.csv`
2. bash: `grep -rn '^A-100,' 采购`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. A-100 哪家报价最低？把默认供应商表和每天的下单表都换成它
2. 找出 A-100 的最低单价供应商，默认供应商和下单目录里每天的 A-100 都改成这家和它的价格
3. 货号 A-100（不含 A-1000、A-100X）谁最便宜？更新默认供应商与各天下单表
4. 比较各家 A-100 的单价，选最低的，把采购目录下所有文件里 A-100 的供应商（和下单单价）更新
5. Who quotes the lowest price for exactly A-100? Switch A-100 in the default-supplier file and every daily order sheet to that supplier and price.
