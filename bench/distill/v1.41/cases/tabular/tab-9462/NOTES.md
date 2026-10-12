## Traps
- Turn 1: exact answer 57; the loose reading (prefix match on route and status) gives 133.
- Turn 2: exact answer 22; the loose reading (route prefix match includes PEK-CAN2) gives 28.
- TR-MULTISRC: 3 files; the first file alone gives 10.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat flights/*.dat | awk -F';' '$2=="PEK-CAN" && $3=="DELAYED" {c++} END{print c+0}'` -> 57
Turn 2: bash: `cat flights/*.dat | awk -F';' '$2=="PEK-CAN" && $3=="CANCELLED" {print $1}' | sort -u | wc -l` -> 22
Final answer: 22 different PEK-CAN flights were cancelled.

## Why the answer is unique
route and status are whole-value columns. The README (flights/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of distinct flights with status CANCELLED on route PEK-CAN.
2. How many unique flight numbers were cancelled on PEK-CAN (PEK-CAN2 excluded)?
3. Across mon, tue and wed, count each cancelled PEK-CAN flight once.
4. Per README, how many different flights on PEK-CAN have status CANCELLED?
5. De-duplicated count of CANCELLED flights for the PEK-CAN route.
