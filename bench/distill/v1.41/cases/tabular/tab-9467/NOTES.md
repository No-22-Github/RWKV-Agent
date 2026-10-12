## Traps
- Turn 1: exact answer 2025; the loose reading (prefix match on station and quality) gives 4414.
- Turn 2: exact answer 2357; the loose reading (quality prefix match) gives 3192.
- Turn 3: exact answer 1057; the loose reading (station prefix match includes XH-1) gives 1222.
- TR-MULTISRC: 3 files; the first file alone gives 432.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat rain/*.txt | awk -F',' '$2=="XH-1" && $4=="ok" {s+=$3} END{print s}'` -> 2025
Turn 2: bash: `cat rain/*.txt | awk -F',' '$2=="XH-2" && $4=="ok" {s+=$3} END{print s}'` -> 2357
Turn 3: bash: `cat rain/*.txt | awk -F',' '$2=="XH-10" && $4=="ok" {a+=$3} $2=="XH-2" && $4=="ok" {b+=$3} END{d=a-b; if (d<0) d=-d; print d}'` -> 1057
Final answer: XH-10 and XH-2 differ by 1057 mm.

## Why the answer is unique
station and quality are whole-value columns. The README (rain/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. How many mm apart are the ok-quality rainfall totals of XH-10 and XH-2?
2. Compute XH-10's rainfall total and give me its gap to XH-2's.
3. Absolute difference between the XH-10 total and the XH-2 total (quality ok only).
4. By how much does XH-10 differ from XH-2 in total ok rainfall?
5. Work out XH-10's total, then subtract XH-2's and drop the sign.
