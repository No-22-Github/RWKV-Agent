## Traps
- TR-TZ: support/calls-2026-09.csv stamps calls in UTC while the README fixes the Singapore
  team's window to 09:00-18:00 local (UTC+8), i.e. UTC 01:00-09:59. Reading 09:00-18:00 off
  the UTC hours gives 8 calls instead of 13.

## Reference solution
1. read_file README.md: stamps are UTC; the Singapore window is 09:00-18:00 local (UTC+8).
2. read_file support/calls-2026-09.csv. Turn 1: 34 calls in September. Turn 2: shift each stamp by +8h; 19 calls open inside the local working window.
3. Turn 3: winch leads the Singapore-hours calls (13 of 19, ahead of windlass 3, thruster 2, autopilot 1).

## Why the answer is unique
The UTC hours 10:00-17:59 look like working hours naively (9 calls), but in Singapore those are 18:00-01:59; the README's UTC+8 note moves the window to UTC 01:00-09:59, which holds exactly 19 calls. Within them winch appears 13 times, ahead of every other line, so 34, 19 and winch are the only readings.

## Five alternative phrasings of the task
1. tansley maritime september support calls
2. call volume for september
3. calls inside the singapore team's hours
4. product line behind the singapore-hours calls
5. september support log by product line
