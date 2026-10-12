## Traps
- TR-DECOY: only 状态=已退款 rows count (驳回 and 处理中 are not refunds). TR-READONLY: other stores keep 关注：否 in every sheet (门店/README.md); the board edit is one line per file, selected by store name.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in 退款/*.csv; do echo "$f $(awk -F, '$4=="已退款" {s+=$3} END{print s}' $f)"; done`
Turn 2 (edit, reply DONE):
1. bash: `sed -i '/^西湖店 /s/关注：否/关注：是/' 门店/看板/*.txt && sed -i 's/^关注：否$/关注：是/' 门店/档案/西湖店.md`
2. bash: `grep -rn 西湖店 门店`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 已退款金额最高的是哪家店？在看板各周和它的档案里把关注改成是
2. 按已退款合计找出退款最多的门店，把它标为重点关注（看板四周的表与档案）
3. 哪家门店退款金额最大（只看已退款）？把看板每周表里它那一行和它的档案都改成关注：是
4. 统计各店已退款金额，对最高的那家把关注状态设为是，看板和档案要一致
5. Which store has the highest total of refunded rows? Mark it as watched in every weekly board sheet and in its profile.
