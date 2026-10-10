## Traps
- TR-TZ: hyd-roam stamps UTC while every other writer stamps British Summer Time, so identical stamps belong to different UTC moments. Counting stamps without the one-hour shift folds in 9 non-roam alarms stamped 15:30-16:15 (UTC 14:30-15:15) and answers 16; shifting per the README gives 19.

## Reference solution
1. Read README.md: line grammar and the hyd-roam clock convention.
2. Search 'pump stall' and read the line windows around the hits.
3. Convert each writer's stamp to UTC (hyd-roam as-is, the others minus one hour).
4. Keep ERROR alarms with UTC time in 15:30:00-16:15:00; the count is 19.

## Why the answer is unique
The README names hyd-roam as the only UTC writer, so the conversion is exact; the level and message opening admit only pump-stall ERRORs. The shifted window yields 19.
