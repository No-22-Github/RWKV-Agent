## Traps
- TR-DECOY: UPLOAD_LIMIT_MB also has 512. Target line: `CACHE_MB=512      # per worker` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read app/.env; locate the target line `CACHE_MB=512      # per worker`.
3. replace_lines that single line with `CACHE_MB=768      # per worker` (only 512 -> 768).
4. Read app/.env back and confirm only that line changed.
Final answer: 'Updated app/.env: the value is now 768, comments and alignment untouched.'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
