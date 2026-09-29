## Traps
- TR-ABSENT: collection_log_2026.csv holds only 2026 rounds, so there is no April 2025 figure to compare with.
  A reader who reports the April 2026 intake instead answers 44218 litres, which is that month's volume rather
  than the difference the request asks for.

## Reference solution
1. List the workspace: collection_log_2026.csv and a short README.md.
2. Read README.md: the tanker telemetry was commissioned in January 2026, so the log begins that month.
3. Read collection_log_2026.csv: every round is dated 2026 and no row carries an April 2025 collection, so the
   April 2025 figure is absent from the table.
4. Answer in prose: "I checked collection_log_2026.csv and README.md — the log starts in January 2026, so there
   is no April 2025 record to compare against and the year-on-year difference cannot be computed." The answer
   names the missing April 2025 figure but gives no substitute number: the April 2026 litres are that month's
   volume, not the difference that was asked for.

## Why the answer is unique
A difference needs both years' figures. The readme states when the log starts and the file carries 2026 rounds
only, so the April 2025 figure is absent from the workspace rather than zero: nothing says the dairy collected
nothing that month. Reporting the April 2026 volume, or treating the difference as nil, would assert something
the files do not show. Scored with output_contains_any over "April 2025", "Apr 2025" or "2025-04" (the table's
date spelling) and output_excludes keeping out UNKNOWN and the 2026-only 44218, so the accepted answers are the
ones that name the missing figure.
