## Traps
- bc is not installed (`command not found`, exit 127); the product sum has to be done with awk.
- TR-DECOY: lines starting with # are retired items (采购/说明.md); summing every line gives 29100.72.

## Reference solution
1. bash: the tool the user named -> exit 127 (`command not found`).
2. bash: `grep -v '^#' 采购/清单.txt | awk '{s+=$2*$3} END{printf "%.2f\n", s}'`
Final answer: 采购总额是 22971.29 元（bc 不可用，我用 awk 算的；以 # 开头的已停用条目没有计入）。

## Why the answer is unique
The script or query text in the fixture fixes the filter exactly; the fallback reproduces it with awk.

## Five alternative phrasings of the task
1. 帮我用 bc 算 采购/清单.txt 的总额：每行数量×单价，加总，已停用的行除外。
2. 采购清单的总金额是多少元？用 bc 计算，规则看采购/说明.md。
3. 用 bc 计算 清单.txt 里所有有效条目的 数量×单价 之和。
4. 按 说明.md 的口径，用 bc 把采购清单合计一下，告诉我多少元。
5. 请用 bc 把采购清单每行的金额加起来，# 开头的不算，总额是多少？
