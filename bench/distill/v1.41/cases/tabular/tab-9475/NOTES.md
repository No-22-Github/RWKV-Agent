## Traps
- Turn 1: exact answer 44702; the loose reading (prefix match on merchant and result) gives 96779.
- Turn 2: exact answer 35669; the loose reading (prefix match on merchant and result) gives 85308.
- Turn 3: exact answer 11775; the loose reading (result prefix match includes ok-review) gives 23237.
- TR-TRUNC: the file is 83KB and 1210 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F',' '$2=="M-17" && $3=="card" && $4=="ok" {s+=$5} END{print s}' pay/txns.txt` -> 44702
Turn 2: bash: `awk -F',' '$2=="M-17" && $3=="wallet" && $4=="ok" {s+=$5} END{print s}' pay/txns.txt` -> 35669
Turn 3: bash: `awk -F',' '$2=="M-18" && $3=="wallet" && $4=="ok" {a+=$5} $2=="M-17" && $3=="wallet" && $4=="ok" {b+=$5} END{d=a-b; if (d<0) d=-d; print d}' pay/txns.txt` -> 11775
Final answer: M-18 and M-17 wallet totals differ by 11775 yuan.

## Why the answer is unique
merchant, method and result are whole-value columns. The README (pay/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. What is the gap between M-18's wallet total and M-17's?
2. Compute M-18's settled wallet amount, then give me its difference to M-17's.
3. By how many yuan do the M-18 and M-17 wallet totals differ?
4. Absolute difference of the settled wallet totals, M-18 versus M-17.
5. Work out M-18's wallet total and subtract M-17's, dropping the sign.
