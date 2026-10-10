## Traps
- 日志里有只差一两个词的相似行（别的对象、别的状态、检查/重试类提及），按关键词模糊找容易落到它们头上；目标短语是 `job eod-settlement exited code=137`（模式 unique）。
- 文件大多超过 read_file 的 64 KiB 上限，整读不完整，也不该靠数行。

## Reference solution
1. search_text 搜完整短语，结果自带行号；按题面要求取最先（或最后、唯一）一处：第 427 行。
终答一句话：目标事件在第 427 行。判据：任一行号写法（第 N 行 / N 行 / line N 等）；用过 search_text；read_file 最多 1 次。
答案 427。

## Why the answer is unique
完整短语只出现在预期的那几行，题面指定取第一次 / 最后一次 / 唯一一次，因此行号唯一。
