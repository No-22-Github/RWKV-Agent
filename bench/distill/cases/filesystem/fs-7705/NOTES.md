## Traps
- TR-DECOY: permits/2025/camping-permit-may.txt is last season's permit for the same zone, valid 2025-05-23 to 2025-05-26. Quoting those dates as the club's current cover reports an expired permit as valid; README says 2025 is closed and archived and only permits under 2026 count for this season.

## Reference solution
1. List permits/: camping-permit-may.txt appears in 2025/ and 2026/.
2. Read README.md: 2025 is closed and archived; only 2026 permits count this season.
3. Read permits/2026/camping-permit-may.txt: valid 2026-05-22 to 2026-05-25, zone Loon Basin; the file in 2025/ is the 2025 backcountry camping permit kept alongside.


> v2（2026-10-01）：判据改写——output_contains 只留专有名词事实，数量事实移入 output_contains_any 并给多种自然写法（原「数字+量词」锚串对自然语言终答过严）。

## Why the answer is unique
The decoy 2025-05-23 is the start date of the archived permit. README marks the 2025 folder closed and says only 2026 permits count for this season's trips, so the current cover can only be the file in permits/2026/, whose validity line reads 2026-05-22 to 2026-05-25 with zone Loon Basin. The old file identifies itself as the 2025 backcountry camping permit on its first line. Season rule plus the permit's own validity line pin all three facts, so no second reading exists.
