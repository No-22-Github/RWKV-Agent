## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `    sampling_percentage: 15   # prod default` ((no section needed)).

## Reference solution
1. Read otel/ask.txt: new value 5
2. Read otel/collector.yaml; locate the target line `    sampling_percentage: 15   # prod default`.
3. replace_lines that single line with `    sampling_percentage: 5   # prod default` (only 15 -> 5).
4. Read otel/collector.yaml back and confirm only that line changed.
Final answer: 'Updated otel/collector.yaml: the value is now 5, comments and alignment untouched.\nDONE'. Criteria: file equals the expected content exactly; output contains DONE.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
