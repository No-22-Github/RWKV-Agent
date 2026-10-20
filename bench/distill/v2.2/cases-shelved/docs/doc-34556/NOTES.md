## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（specs/gateway-requirements.md 466 行、specs/ledger-requirements.md 634 行、specs/notifier-requirements.md 508 行、specs/portal-requirements.md 704 行、specs/scheduler-requirements.md 424 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 must-gaps.md，列出 9 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
12520
(fixture: specs/gateway-requirements.md=3505, specs/ledger-requirements.md=4841, specs/notifier-requirements.md=3842, specs/portal-requirements.md=5346, specs/scheduler-requirements.md=3220)
lines per document: [466, 634, 508, 704, 424]

## Five alternative phrasings of the task
1. Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md.
2. 麻烦帮我：Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md.
3. Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md. (keep it organised)
4. 想请你看看：Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md.
5. 再确认一下：Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md.
