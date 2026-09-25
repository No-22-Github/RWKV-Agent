## Traps
- TR-ABSENT: collection_log_2026.csv holds only 2026 rounds, so there is no April 2025 figure to compare with.
  A reader who reports the April 2026 intake instead answers 44218 litres, which is that month's volume rather
  than the difference the request asks for.

## Reference solution
1. List the workspace: the collection log and a short readme.
2. Read README.md: the tanker telemetry was commissioned in January 2026, so the log begins that month.
3. Read collection_log_2026.csv: every round is dated 2026 and no row carries an April 2025 collection.
4. The comparison cannot be made, so the answer is UNKNOWN.

## Why the answer is unique
A difference needs both years' figures. The readme states when the log starts and the file carries 2026 rounds
only, so the April 2025 figure is absent from the workspace rather than zero: nothing says the dairy collected
nothing that month. Reporting the April 2026 litres, or treating the difference as nil, would assert something
the files do not show, so the only supported answer is UNKNOWN.
