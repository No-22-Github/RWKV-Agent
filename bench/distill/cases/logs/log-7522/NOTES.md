## Traps
- TR-RULEFILE: whether a row counts as slow depends on notes/thresholds.md (reporting-class dbs incl. analytics: dur > 3 s; etl-class: dur > 8 s). Counting everything over 3 seconds regardless of db class gives the recorded decoy 14; applying the sheet gives 11 (reporting 8 + analytics 1 + etl_warehouse 2).

## Reference solution
1. Turn 1: read notes/thresholds.md (alert = reporting-class db with more than 5 slow queries in any 10-minute window), read logs/db-slowquery.log: reporting logs six slow rows between 02:10:12 and 02:18:32, all inside one 10-minute span, which is why the 02:17:03 ALERT fired. Answer: reporting.
2. Turn 2: slow per the sheet: reporting 8 (4.4, 3.4, 3.9, 4.2, 3.6, 5.1, 4.8, 5.5), analytics 1 (6.2), etl_warehouse 2 (12.6, 9.8) = 11. Answer: 11 slow.
3. Turn 3: the longest of those is 12.6 (02:41:17). Answer: 12.6.
4. Turn 4: drop analytics (its one slow row at 03:21:33): 11 - 1 = 10. Answer: 10 slow.

## Why the answer is unique
The sheet defines slow per database class, so the same duration is slow on reporting and harmless on etl_warehouse; every row names its db, and the class map in the sheet is explicit, leaving one total. The ALERT row carries no duration and names no db, so the attribution comes from the window rule: only reporting exceeds five slow queries inside ten minutes (the six rows 02:10:12-02:18:32). The exclusion in turn 4 removes exactly analytics' single slow row.
