## Traps
- TR-READONLY: 订单/模板.csv stays as it is. TR-DECOY: 「待处理-补录」 shares the prefix with 「待处理」 but is a different status (a substring `s/待处理/已受理/` also rewrites it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find 订单 -name '2026-*.csv' | xargs sed -i 's/,待处理$/,已受理/'`
2. bash: `grep -rc 已受理 订单`
Turn 2:
1. bash: `sed -i 's/,已受理$/,待处理/' 订单/2026-08.csv 订单/2026-09.csv`
2. bash: `grep -rc 已受理 订单`
Final answers: DONE (turn 1: 七月、八月、九月的待处理订单已受理; turn 2: 八月九月又变回待处理，七月仍是已受理).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. 订单表里待处理的全部标成已受理，九月那份再还原
2. 把各月待处理订单批量改为已受理（模板和补录状态除外），之后九月恢复原状
3. 待处理→已受理，九月撤销
4. 各月订单状态改成已受理；九月因为没对账改回待处理
5. Mark every pending order as accepted in the monthly files, then undo it for September.
