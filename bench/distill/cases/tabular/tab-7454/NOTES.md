## Traps
- TR-DECOY：冻品组里有 4 行「鲜切鱼片」，品名里带「鲜」字，不注意会把它们并进鲜货组，得 5910.09；README 写明组别按柜台划分，鲜切鱼片是冻品组的加工品。

## Reference solution
1. 读 README.md：组别按柜台划分，鲜切鱼片属于冻品组。
2. 查询：{"path":"data/seafood_sales_2026-08.csv","filter":{"组别":"鲜货组"},"operation":"sum","field":"金额"}，得 4471.76。
3. 终答只给数字 4471.76。

## Why the answer is unique
按组别列过滤是唯一与 README 口径一致的读法；把鲜切鱼片并进来的读法与 README 相矛盾（它们在冻品组），不成立。其余组别与日期都不在口径内。答案唯一为 4471.76。
