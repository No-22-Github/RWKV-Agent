## Traps
- None.

## Reference solution
1. 读 配置/存储集群.yaml：12 节点 × 8 盘 × 7.68 TB，3 副本，预留 0.15。
2. calculator：12 * 8 * 7.68 / 3 * (1 - 0.15)，precision 1 → 208.9。
终答一句话：可用容量约 208.9 TB（裸容量 737.28 TB ÷ 3 副本，再扣 15% 预留）。判据：包含 208.9，调用过 calculator。

## Why the answer is unique
公式在 README 给出，参数都在配置里。
