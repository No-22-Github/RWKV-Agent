## Traps
TR-TRUNC, TR-DECOY

## Reference solution
list_files 看各文件行数（change-board/platform-change-requests.md 669 行、change-board/data-change-requests.md 774 行、change-board/mobile-change-requests.md 599 行）
search_text / bash grep 定位级别为高的条目，再读对应位置确认状态
read_file 用 start_line/end_line 读相关片段，约 4 次
write_file 写入 cab-agenda-major.md，列出 7 个编号
作答。

## Why the answer is unique
Target entries are the only ones with level high, status open; decoys differ in exactly one field.

## Estimated trajectory tokens
12460
(fixture: change-board/platform-change-requests.md=5212, change-board/data-change-requests.md=6102, change-board/mobile-change-requests.md=4706)
lines per document: [669, 774, 599]

## Five alternative phrasings of the task
1. I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md.
2. 麻烦帮我：I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md.
3. I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md. (keep it organised)
4. 想请你看看：I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md.
5. 再确认一下：I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md.
