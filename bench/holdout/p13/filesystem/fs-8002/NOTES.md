## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的自然语言导览，必须落在目录的真实内容上：README 说明这是 Q3 planning 的共享目录；budget-2026.csv 是预算数字（分类/负责人/Q3 金额）；action-items.txt 是带 owner 和期限的行动项。只报文件名而不说用途、或指错数字所在文件的答案过不了判据。

## Reference solution
1. 列目录 / 读 README.md：Q3 planning 工作目录，预算 workbook 以 CSV 导出，行动项在文本文件里（1–2 次调用）。
2. 读 budget-2026.csv 与 action-items.txt 抽一眼内容（1–2 次调用）。
3. 终答（英文，自然语言 3–5 句）：three files - a README describing the Q3 planning folder, budget-2026.csv holding the Q3 money figures by category and owner, and the action items file listing who owes what by when; the Q3 numbers are in budget-2026.csv.

## Why the answer is unique
三个文件角色互斥且由内容唯一决定：README 自述用途，CSV 的表头是 category/owner/amount_q3，txt 的行是 action item 加 owner 和期限。判据的必含事实（budget-2026.csv、action、Q3）要求答案既点出文件又说到用途；把行动项文件说成数字来源就与两个文件的内容矛盾。
