## Traps
- TR-DECOY: logs/board-2026-09.log opens with a warning about
  rooms/2026-08.csv being cleaned up under the retention policy; chasing that
  line instead of the IndexError below it "fixes" a routine cleanup and
  leaves the crash in place.

## Reference solution
1. Read logs/board-2026-09.log: the failure is an IndexError at board.py
   line 23 (fee = int(row[3])).
2. Read board.py and its notes: rooms/ exports end with a 小计 summary row
   that only carries three fields.
3. Read rooms/2026-09.csv and confirm the last row (小计,9,12840).
4. Change board.py so summary rows are skipped before the field access; the
   sweep over rooms/*.csv already picks up later months.

## Why the answer is unique
With summary rows skipped, the merged run (the scoring run adds
rooms/2026-10.csv) prints exactly 2026-09-02,2,3160 / 2026-09-05,2,2560 /
2026-09-12,2,2380 / 2026-09-20,3,4740 / 2026-10-03,3,3540 / 2026-10-15,1,1190
and 合计,13,17570. The August warning is a retention cleanup, not a fault:
the export is gone on purpose and the script already globs whatever months
are present, so no change there can alter the sheet. Keeping the summary row
in the aggregation is the only way to preserve the IndexError, and dropping
data rows would change the day lines the layout requires.
