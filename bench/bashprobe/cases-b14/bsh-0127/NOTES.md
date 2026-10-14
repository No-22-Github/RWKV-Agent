## Traps
- TR-DECOY: matching '*.csv*' (temp files counted) gives 72; the README's rule gives 51.
- 224 files in nested folders under 数据/, so counting by listing is not practical.

## Reference solution
Turn 1: bash: `find 数据 -type f -name '*.csv' | wc -l` -> 118
Turn 2: bash: `find 数据 -type f -name '*2025*.csv' | wc -l` -> 51
Final answer: 文件名带 2025 的 CSV 有 51 个。

## Why the answer is unique
The README fixes which names count; matching by that rule over the whole tree gives one number.
