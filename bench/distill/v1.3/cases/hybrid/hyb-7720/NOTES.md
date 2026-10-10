## Traps
- TR-TZ: the log is stamped in UTC and the README pins the tariff window to plant time
  (UTC+1). Local 23:00-07:00 equals UTC 22:00-06:00; reading 23:00-07:00 off the UTC hours
  gives 9 starts instead of 11.

## Reference solution
1. read_file README.md: stamps are UTC; the night tariff is 23:00-07:00 plant time (UTC+1).
2. read_file logs/compressor-2026-09.log. Turn 1: shift each stamp by +1h; 11 starts fall inside 23:00-05:59 plant time. Turn 2: the 22:00-08:00 window adds the 21:10Z and 06:20Z starts, for 13.
3. Turn 3: unitC owns 5 of the 11 starts in the original window, ahead of unitA and unitB (3 each).

## Why the answer is unique
The 22:xx UTC starts sit inside the local tariff night but outside a naive UTC reading, and the 06:20Z start sits outside the local window but inside the naive one, so the naive count is 9 while the plant-time count is 11 - the README fixes the clock to plant time. Widening to 22:00-08:00 local adds exactly two starts, giving 13; within the original window unitC leads 5 to 3.

## Five alternative phrasings of the task
1. hargate cold storage compressor starts september
2. starts inside the night tariff window
3. compressor starts on the widened tariff night
4. which unit started most in the tariff nights
5. september compressor log by unit and window
