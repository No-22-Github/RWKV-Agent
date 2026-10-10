## Traps
- 无。

## Reference solution
1. data_query：堆场/过磅记录.csv，filter 船次=HX-2612，sum 毛重(磅)。
2. calculator：合计 × 0.45359237，precision 1 → 201190.9。
终答示例：HX-2612 船次集装箱总重约 201190.9 公斤（磅数合计 × 0.45359237）。。判据：包含 201190.9（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
船次过滤精确，换算系数与位数由题面给定。
