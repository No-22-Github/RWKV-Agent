## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `min_client = "2.4.1"   # first build with the new auth flow` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read pkg/release.toml; locate the target line `min_client = "2.4.1"   # first build with the new auth flow`.
3. replace_lines that single line with `min_client = "2.5.0"   # first build with the new auth flow` (only 2.4.1 -> 2.5.0).
4. Read pkg/release.toml back and confirm only that line changed.
Final answer: 'Updated pkg/release.toml: the value is now 2.5.0, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
