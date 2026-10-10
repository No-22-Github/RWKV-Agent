## Traps
- 无。

## Reference solution
1. read_file 印务/纸张规格.md：整张 880 × 1230 mm，80 g/㎡，每令 500 张。
2. calculator：3 * 500 * 0.88 * 1.23 * 80 / 1000 = 129.89。
终答示例：129.89。判据：expected_number 129.89，调用过 calculator。

## Why the answer is unique
面积（㎡）× 克重得单张克数，再乘张数换算成公斤。
