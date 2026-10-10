## Traps
- TR-READONLY: 只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。 Target line: `INVERTER_POLL_SEC=20     # 厂商建议不低于 10` ((no section needed)).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 采集/inverter.env; locate the target line `INVERTER_POLL_SEC=20     # 厂商建议不低于 10`.
3. replace_lines that single line with `INVERTER_POLL_SEC=15     # 厂商建议不低于 10` (only 20 -> 15).
4. Read 采集/inverter.env back and confirm only that line changed.
Final answer: '已把 采集/inverter.env 里的 INVERTER_POLL_SEC 改成 15，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
