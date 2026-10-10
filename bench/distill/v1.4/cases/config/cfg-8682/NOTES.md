## Traps
- TR-DECOY: plant-bb (+02:00) shares a prefix; plant-a already has +01:00 which was copied into plant-b by mistake.

## Reference solution
1. Read the basis registry/sites.csv: the new value is +03:00.
2. Read config/clock.ini: line 1, `[plant-b]
utc_offset = +01:00`, is the one to change.
3. replace_lines line 1 with `[plant-b]
utc_offset = +03:00`; the rest of the line stays.
4. Read config/clock.ini back to confirm.
Final answer example: plant-b's utc_offset in config/clock.ini is now +03:00 (Nairobi), taken from registry/sites.csv; plant-a is unchanged.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
