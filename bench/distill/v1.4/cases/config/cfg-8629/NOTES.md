## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `DB_POOL_SIZE=20      # per instance; max_connections is 400` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read services/orders/.env.prod; locate the target line `DB_POOL_SIZE=20      # per instance; max_connections is 400`.
3. replace_lines that single line with `DB_POOL_SIZE=30      # per instance; max_connections is 400` (only 20 -> 30).
4. Read services/orders/.env.prod back and confirm only that line changed.
Final answer: 'Updated services/orders/.env.prod: the value is now 30, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
