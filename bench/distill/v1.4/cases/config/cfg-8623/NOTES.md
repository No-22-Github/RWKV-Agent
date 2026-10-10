## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `max_recipients = 100   ; per message` ((no section needed)).

## Reference solution
1. Read changes/CHG-4471.txt: new value 50
2. Read relay/mail.ini; locate the target line `max_recipients = 100   ; per message`.
3. replace_lines that single line with `max_recipients = 50   ; per message` (only 100 -> 50).
4. Read relay/mail.ini back and confirm only that line changed.
Final answer: 'Updated relay/mail.ini: the value is now 50, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
