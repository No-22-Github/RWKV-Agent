## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `poll_every_s = 45     ; lower = more load` ([sync]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read ops/poller.conf.ini; locate the target line `poll_every_s = 45     ; lower = more load`.
3. replace_lines that single line with `poll_every_s = 30     ; lower = more load` (only 45 -> 30).
4. Read ops/poller.conf.ini back and confirm only that line changed.
Final answer: 'Updated ops/poller.conf.ini: the value is now 30, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
