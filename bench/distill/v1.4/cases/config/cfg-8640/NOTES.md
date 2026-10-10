## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `时段分钟 = 40    ; 含洗吹` ([剪发]).

## Reference solution
1. 读 预约/店长留言.txt 取得新值 45
2. Read 预约/时段.ini; locate the target line `时段分钟 = 40    ; 含洗吹`.
3. replace_lines that single line with `时段分钟 = 45    ; 含洗吹` (only 40 -> 45).
4. Read 预约/时段.ini back and confirm only that line changed.
Final answer: '已把 预约/时段.ini 里的 时段分钟 改成 45，注释和缩进没动。\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
