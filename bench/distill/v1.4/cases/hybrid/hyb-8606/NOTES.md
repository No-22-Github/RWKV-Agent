## Traps
- TR-DECOY: The table lists September (13.0, the current value) and August; the gossip post says 11%.

## Reference solution
1. Read the basis https://fjordfreight.eu/surcharges: the new value is 14.5.
2. Read config/shipping.env: line 2, `FUEL_SURCHARGE_PCT=13.0`, is the one to change.
3. replace_lines line 2 with `FUEL_SURCHARGE_PCT=14.5`; the rest of the line stays.
4. Read config/shipping.env back to confirm.
Final answer example: FUEL_SURCHARGE_PCT in config/shipping.env is now 14.5, Fjord Freight's October 2026 surcharge. / DONE
Criteria: exact target file content; output contains DONE.

## Changelog
- v2：S5：依据文件里的新值写的是「自 2026-10-01 起」，而今天是 2026-09-16，老师说「还没生效、不用改」才是对的；生效日改为 2026-09-01（网页发布日期同步提前）。

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.

## Five alternative phrasings of the task
1. Fjord Freight fuel surcharge
2. Fjord Freight surcharge October 2026
3. Fjord Freight surcharges table
4. Fjord Freight official fuel rate
5. Fjord Freight monthly surcharge
