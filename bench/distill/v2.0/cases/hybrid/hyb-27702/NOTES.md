## Traps
- TR-TZ: logs/temp-alerts-2026-09.log stamps every line in UTC while the README pins the
  reporting clock to Beijing time (UTC+8). Counting the 09:00-18:00 window on the raw UTC
  hours gives 3 (10:05Z, 09:15Z, 09:05Z); converting first gives 7.

## Reference solution
1. read_file README.md: the log is UTC, the reporting clock is Beijing time (UTC+8), levels sit in column two.
2. read_file logs/temp-alerts-2026-09.log. Turn 1: 11 ALERT lines. Turn 2: convert each UTC hour to local and keep 09:00-18:00 local, which keeps 7 of the 11. Turn 3: of those 7, 冷库A区 owns 4.

## Why the answer is unique
The naive pass keeps only the lines whose UTC hour already reads 09-17 (3 lines), but the README states the log is UTC and the report clock is Beijing time, so every timestamp must shift by 8 hours first; the 01:xxZ and 02:xxZ alerts land inside the local working window and the 10:05Z alert falls out of it. With the shift applied the working-hour count is 7 and the A-zone share is 4; no other reading is consistent with the stated clocks.

## Five alternative phrasings of the task
1. tiemao cold chain september temperature alerts
2. alert lines in the september temperature log
3. alerts during beijing working hours 09:00-18:00
4. zone A alerts inside the working-hour window
5. september cold storage alerts by shift window
