## Traps
- TR-DECOY: 第 7 行是提到 load_tariff_table 的注释，文件末尾 quote() 里还有一处调用；都不是定义。

## Reference solution
1. search_text 搜「def load_tariff_table」（path billing/tariff.py），结果带行号：第 344 行。
终答一句话：load_tariff_table 定义在 billing/tariff.py 第 344 行（第 7 行的注释和 quote() 里的调用都不是定义）。判据：包含 344（独立词元）；read_file 最多 1 次。

## Why the answer is unique
文件里只有一行以 def load_tariff_table( 开头。
