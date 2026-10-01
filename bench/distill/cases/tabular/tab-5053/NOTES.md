## Traps
- TR-ABSENT: sailings_2026.csv holds 2026 sailings only, so there is no June 2025 figure to compare with. A reader who reports the June 2026 traffic instead answers 252 vehicles, which is that month's count rather than the change the request asks for.

## Reference solution
1. List the workspace: sailings_2026.csv and a short README.md.
2. Read README.md: the company changed hands in January 2026 and the log starts with that season.
3. Read sailings_2026.csv: every crossing is dated 2026 and no row carries a June 2025 sailing, so the June 2025
   figure is absent from the table.
4. Answer in prose: "I checked sailings_2026.csv and README.md — the log only starts with the 2026 season, so
   there is no June 2025 sailing to compare against and the season-on-season change cannot be computed." The
   answer names the missing June 2025 figure but gives no substitute number: the June 2026 vehicle count is that
   month's traffic, not the change that was asked for.

## Why the answer is unique
A change needs both seasons' figures. The readme states when the log starts and the file carries 2026 sailings
only, so the June 2025 count is absent from the workspace rather than zero: nothing says the ferry carried no
vehicles that month. Reporting the June 2026 traffic, or treating the change as nil, would assert something the
files do not show. Scored with output_contains_any over "June 2025", "Jun 2025" or "2025-06" (the table's date
spelling) and output_excludes keeping out UNKNOWN and the 2026-only 252, so the accepted answers are the ones
that name the missing figure.
