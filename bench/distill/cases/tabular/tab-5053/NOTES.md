## Traps
- TR-ABSENT: sailings_2026.csv holds 2026 sailings only, so there is no June 2025 figure to compare with. A reader who reports the June 2026 traffic instead answers 252 vehicles, which is that month's count rather than the change the request asks for.

## Reference solution
1. List the workspace: the sailing log and a short readme.
2. Read README.md: the company changed hands in January 2026 and the log starts with that season.
3. Read sailings_2026.csv: every crossing is dated 2026 and no row carries a June 2025 sailing, so the comparison cannot be made and the answer is UNKNOWN.

## Why the answer is unique
A change needs both seasons' figures. The readme states when the log starts and the file carries 2026 sailings only, so the June 2025 count is absent from the workspace rather than zero: nothing says the ferry carried no vehicles that month. Reporting the June 2026 traffic, or treating the change as nil, would assert something the files do not show, so the only supported answer is UNKNOWN.
