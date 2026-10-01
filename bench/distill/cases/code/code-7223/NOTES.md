## Traps
- TR-NEARNAME: 仓库里同时存在名字相近的 order_utils.py，不注意会答它；它与冻结无关，也没有 freeze_batch。

## Reference solution
1. 读题面点名的 stock_compare.py，看到 `from orders_util import freeze_batch`。
2. 打开 orders_util.py 确认 `def freeze_batch`。
3. 作答 orders_util.py。

## Why the answer is unique
order_utils.py 只定义 order_fee_summary 与 order_count_by_store，全仓库 `def freeze_batch` 只在 orders_util.py 出现一处；import 语句也指向 orders_util。答案唯一。

## 正确答案
orders_util.py
