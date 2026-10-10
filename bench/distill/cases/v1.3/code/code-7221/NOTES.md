## Traps
- 无陷阱（L0 基题）。干扰只是三个文件并列，`sync_cli.py` 与 `models.py` 里都没有该函数的 `def`。

## Reference solution
1. 在仓库里搜索 pick_alternate_sku，命中 replenish.py 的定义行与 sync_cli.py 的 import、调用。
2. 确认 `def pick_alternate_sku` 只出现在 replenish.py，作答。

## Why the answer is unique
sync_cli.py 只有 `from replenish import ...` 和调用，没有同名定义；models.py 只有一个数据类。ast 层面 `def pick_alternate_sku` 全仓库恰有一处，答案唯一。

## 正确答案
replenish.py
