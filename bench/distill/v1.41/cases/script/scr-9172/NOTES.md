## Traps
- python3 is not installed (`command not found`, exit 127); the script has to be read and its filter redone with awk.
- TR-DECOY: the script uses a strict `> 3`; `>= 3` gives 84, and counting delivered_partial rows gives 99.
- awk compares the header text with 3 as a string, so the header row has to be excluded.

## Reference solution
1. bash: the tool the user named -> exit 127 (`command not found`).
2. bash: `cat data/orders-*.csv | awk -F, '$1!="order_id" && $3=="delivered" && $4>3' | wc -l`
Final answer: 脚本会打印「延迟订单数: 61」（python3 不可用，我按脚本里的条件用 awk 复算：状态恰好是 delivered 且延迟大于 3 天）。

## Why the answer is unique
The script or query text in the fixture fixes the filter exactly; the fallback reproduces it with awk.

## Five alternative phrasings of the task
1. 执行 tools/slow_orders.py（python3），告诉我输出的延迟订单数是多少。
2. 跑一下 python3 tools/slow_orders.py，结果里的延迟订单数是几？
3. 帮我用 python3 运行 slow_orders.py，把打印出来的数字告诉我。
4. tools 里那个统计延迟订单的 python 脚本跑出来是多少？
5. 运行 slow_orders.py 并告诉我它输出的延迟订单数。
