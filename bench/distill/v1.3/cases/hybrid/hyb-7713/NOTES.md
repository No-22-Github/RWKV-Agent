## Traps
- TR-TZ: the log is stamped in UTC and the README pins schedules and reports to local time
  (UTC+8). The local-night window (22:00-06:00) equals UTC 14:00-22:00; reading the night
  window straight off the UTC hours gives 9 alerts instead of 6, and grouping by UTC date
  puts the peak on 11 September instead of 12 September.

## Reference solution
1. read_file README.md: stamps are UTC, reports follow local time (UTC+8), levels sit at the end of each line.
2. read_file logs/humidity-alerts-2026-09.log. Turn 1: 23 lines end with 告警. Turn 2: convert each stamp to local and keep 22:00-05:59 local, which keeps 6.
3. Turn 3: by local date the night alerts fall on 5, 11, 12, 12, 25, 30 September, so 12 September (20260912) is the peak with two.

## Why the answer is unique
The naive UTC night window catches 9 alerts, but the README fixes the reporting clock to local time, and the 14:xx-21:xx UTC stamps are the ones that convert into the local night. Under the conversion exactly 6 alerts qualify, their local dates are 5, 11, 12, 12, 25 and 30 September, and only 12 September repeats, so the peak day is 20260912.

## Five alternative phrasings of the task
1. qingya tea estate september humidity alerts
2. how many humidity alerts fired in september
3. alerts inside the local night window
4. which local day had the most night alerts
5. september humidity log by local date
