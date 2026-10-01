## Traps
- TR-SIGN: the README defines temp_delta_c as target minus measured, so positive means COLDER than target and 偏高 (above target) is the NEGATIVE rows. Reading the sign intuitively (counting positive deltas) gives the recorded decoy 5; the correct window count is 7 negative rows.

## Reference solution
1. Turn 1: read README.md (delta = target − measured; negative = above target), read logs/telemetry-0926.jsonl, count 冷库A rows in [08:00:00, 12:00:00) with temp_delta_c < 0: -3.8, -1.2, -1.5, -0.9, -1.8, -2.2, -2.6 = 7. Answer: 7 条.
2. Turn 2: of those seven, three are defrost rows (-1.5, -2.2, -2.6); excluding them: 4. Answer: 4 条.
3. Turn 3: status=defrost rows across the day: 05:12:40, 06:47:15, 09:33:44, 10:41:33, 11:20:18, 13:05:00, 14:22:49, 18:09:58, 19:30:25 = 9. Answer: 9 条.
4. Turn 4: among the four kept rows the largest deviation from target is 3.8 (08:12:11). Answer: 3.8.

## Why the answer is unique
The README pins the sign convention, so "偏高" selects exactly the negative rows and the intuitive positive reading is the recorded decoy; each row carries one site, one delta and one status. The defrost exclusion removes exactly the three negative defrost rows in the window, the all-day defrost tally is a direct status count (all nine fall on 冷库A, none on the 冷库B noise rows), and 3.8 is the maximum absolute delta among the four survivors.
