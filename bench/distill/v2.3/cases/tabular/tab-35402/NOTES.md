## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: calculator).

## Reference solution
bash: awk -F, 'NR>1{s+=$2*$3} END{printf "%.2f\n", s*0.92}' 采购/2026q3-办公耗材申购.csv -> 2019.49

## Why the answer is unique
10 行，数量乘单价求和再乘 0.92，verify 从 fixture 重算。

Expected: 2019.49 | 2,019.49
