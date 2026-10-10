## Traps
- TR-TZ: logs/berth-log-2026-09.txt stamps berthings in UTC while the README fixes the
  statistics clock to local port time (UTC+8). Counting rows dated 09-08 gives 10; converting
  first gives 12, because the 09-07 17:40Z and 19:05Z rows fall on local 8 September.

## Reference solution
1. read_file README.md: stamps are UTC; production statistics follow local port time (UTC+8).
2. read_file logs/berth-log-2026-09.txt. Turn 1: shift every stamp by +8h; local 8 September holds 12 berthings. Turn 2: recheck - the 09-07 17:40Z and 19:05Z rows convert to 8 September 01:40 and 03:05 local, so 12 stands; cite the shifted rows, do not adopt the user's figure.
3. Turn 3: of the 12, A 区 owns 6.

## Why the answer is unique
Ten rows carry the 09-08 UTC date, but the README pins the counting clock to local port time, and two of the 12 came in at UTC times that straddle midnight into local 8 September while two late-UTC 8 September rows slide to local 9 September; the converted day holds exactly 12. The reply should prove it from the shifted rows rather than echo the user's figure. Six of the twelve berthings sit in A 区.

## Five alternative phrasings of the task
1. lanwan shipping september berth log statistics
2. ships berthed on local 8 september
3. berthing count in local port time
4. zone A berthings on the eighth
5. september berth log by local day
