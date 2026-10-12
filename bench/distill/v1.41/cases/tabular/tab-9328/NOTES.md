## Traps
- TR-DECOY: exact answer 2026-10-03T23:28; the loose reading (station prefix match, includes N-120) gives 2026-10-03T05:39. Several rows share the extreme value; file order would give 2026-10-01T18:46, the README rule gives 2026-10-03T23:28.
- TR-MULTISRC: 3 files; the first file alone gives 2026-10-01T18:46.

## Reference solution
Turn 1: bash: `cat gusts/*.dat | awk '$2=="N-12" {print $3, $1}' | sort -k1,1nr -k2,2r | head -1` -> 2026-10-03T23:28
        then `cat gusts/*.dat | awk '$2=="N-12"' | wc -l` for the row count asked in the prompt (181)
Final answer: The strongest N-12 gust was at 2026-10-03T23:28; N-12 has 181 readings in total.

## Why the answer is unique
station is a whole-value column; the peak value is shared by several rows and the README picks the latest time. The README (gusts/README.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. When did N-12 record its peak gust? Use the README's tie rule.
2. Timestamp of the highest gust for station N-12 in gusts/ (latest one if tied).
3. Which time shows the maximum gust_kmh for N-12 over the three days?
4. Find the moment of N-12's top gust, breaking ties as the README says.
5. Across day1 to day3, what is the timestamp of the strongest N-12 reading?
