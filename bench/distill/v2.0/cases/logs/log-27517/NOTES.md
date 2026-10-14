## Traps
- TR-DATEFMT: TH-0087 stamps its rows as 日-月-年 ("26-09-2026 08:52:40+08:00", README), all other sensors use ISO. Reading only the ISO rows drops TH-0087's two warm readings in the window (08:52:40, 10:31:22) and its two defrost rows, giving the decoy 7 for turn 1 instead of 9.

## Reference solution
1. Turn 1: read README.md (TH-0087 uses 日-月-年, same day), read logs/telemetry-0926.jsonl, count 冷库B rows with 08:00:00 <= ts < 12:00:00 and temp_c > -18: TH-0114 x4 (08:41:11, 09:23:05, 10:05:12, 11:12:48), TH-0087 x2 (08:52:40, 10:31:22), TH-0203 x3 (09:02:33, 10:44:19, 11:38:55) = 9. Answer: 9 条.
2. Turn 2: per-sensor split of those nine: TH-0114 4, TH-0203 3, TH-0087 2. Answer: TH-0114.
3. Turn 3: TH-0114's first reading above -18 inside [08:00:00, 12:00:00) is 08:41:11. Answer: 08:41 (08:41:11).
4. Turn 4: among TH-0114's in-window warm readings the highest temp is -15.2 (10:05:12). Answer: -15.2.
5. Turn 5: status=defrost rows across the whole day: 05:12:40, 06:47:15, 13:05:00, 14:22:33, 15:41:08, 18:09:52, 19:30:26, 21:14:03, 22:48:41 = 9 (two of them on TH-0087's legacy timestamps). Answer: 9 条.

## Why the answer is unique
The README states both timestamp spellings belong to the same day, so a single reading order governs every window: parse 日-月-年 as day-month and every count has one value. Each row carries one site, sensor, temperature and status; the per-sensor split of the nine warm readings is 4-3-2 with no tie, the in-window first warm reading is unambiguous, and the defrost tally is a direct status count.
