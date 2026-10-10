## Traps
- TR-TZ: telemetry/weighbridge-2026-09.csv stamps crossings in UTC while the README pins
  shift windows to Sydney time (UTC+10). Reading the 06:00-18:00 window straight off the UTC
  hours gives 5; converting first gives 13.

## Reference solution
1. read_file README.md: stamps are UTC, shifts follow Sydney time (UTC+10).
2. read_file telemetry/weighbridge-2026-09.csv. Turn 1: crossings whose local time is 06:00-17:59 number 13. Turn 2: opening the shift at 05:00 local adds the 19:30Z crossing (05:30 local), for 14.
3. Turn 3: M. Okonkwo owns 5 of the 13 day-shift crossings, more than any other driver.

## Why the answer is unique
The UTC hours 08:30, 11:45, 12:15, 06:40 and 04:20 all read as day shift naively, but in Sydney time they are evening, night or late-night crossings, and the README fixes the shift clock to Sydney time. With the conversion, 13 crossings fall in 06:00-17:59 local and exactly one more (19:30Z = 05:30 local) enters under the corrected 05:00 opening, so 13 then 14 are the only readings; Okonkwo leads 5 to 4.

## Five alternative phrasings of the task
1. drayford haulage weighbridge september crossings
2. crossings during the sydney day shift
3. day shift count with the 05:00 gate opening
4. which driver crossed most during day shifts
5. september weighbridge log by local shift
