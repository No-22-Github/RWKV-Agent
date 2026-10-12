## Traps
- Turn 1: exact answer 2264; the loose reading (品种、结算前缀匹配) gives 5711.
- Turn 2: exact answer 407; the loose reading (三列都是前缀匹配) gives 2714.
- Turn 3: exact answer 651; the loose reading (三列都是前缀匹配) gives 502.
- TR-MULTISRC: 3 files; the first file alone gives 25.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 果品批发/*.dat | awk -F';' '$2=="红富士" && $5=="已结" {s+=$4} END{print s}'` -> 2264
Turn 2: bash: `cat 果品批发/*.dat | awk -F';' '$2=="红富士" && $5=="已结" && $3=="烟台" {s+=$4} END{print s}'` -> 407
Turn 3: bash: `cat 果品批发/*.dat | awk -F';' '$2=="红富士" && $5=="已结" && $3=="洛川" {a+=$4} $2=="红富士" && $5=="已结" && $3=="烟台" {b+=$4} END{d=a-b; if (d<0) d=-d; print d}'` -> 651
Final answer: 洛川和烟台的已结箱数相差 651 箱。

## Why the answer is unique
品种, 产地 and 结算 are whole-value columns. The README (果品批发/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 洛川产红富士已结箱数和烟台的差多少？
2. 算出洛川的已结红富士箱数，再给我它与烟台的差值。
3. 两个产地（洛川、烟台）的红富士已结箱数相差多少箱？
4. 洛川比烟台多或少多少箱，取绝对值。
5. 同样口径下洛川合计减去烟台合计，绝对值是多少？
