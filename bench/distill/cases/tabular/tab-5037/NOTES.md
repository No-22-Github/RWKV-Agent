## Traps
- TR-DUPROW: 2 rounds in the March 2026 export were written out a second time, each repeating its
  collection_id, date, round and litres, so adding every March 2026 line gives a change of 19526 litres instead of
  6559.

## Reference solution
1. List the workspace: the two-season collection log and a short readme.
2. Read README.md: one row per round, and the March export was re-run after a failed backup.
3. Read collection_log_2025_2026.csv and add the litres per month, counting one line per collection_id.
4. March 2025 comes to 43345 litres and March 2026 to 49904 litres, a change of 6559 litres.

## Why the answer is unique
The readme says one row per round and explains the second export, and each reprinted line repeats its
collection_id and every other field, so the repeats are the same collection written out twice rather than
additional milk. Counting the distinct March 2026 rounds against the March 2025 rounds gives a change of 6559
litres, and the March 2025 lines carry no repeats to strip out.
