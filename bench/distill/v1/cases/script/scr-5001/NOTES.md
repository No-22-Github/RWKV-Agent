## Traps
- TR-DEFN: the statement's figures are the loads the studio billed, not the rows that sit in the kiln room log. firings/2026-09.csv keeps two loads that were booked and cancelled (Bergamot Studio on 2026-09-09, Thistle and Fern on 2026-09-22, both status void) and the October log adds a third (Thistle and Fern on 2026-10-06). README.md says a void row stays in the log but is never charged, and that the statement counts billed loads. statement.py tests `row["status"] == "voided"`, which never matches the log's `void`, so all three cancelled loads are billed: the script prints `TOTAL,10,210.00` where the statement has to read `TOTAL,7,122.50`. trap_decoys records that raw total, the answer a solver gets by leaving the skip test alone or by rewriting the script from the log alone.

## Reference solution
1. Read README.md: a void row is a cancelled load with no charge, the statement lists billed loads per client in name order, and amounts print in pounds with two decimals.
2. Read firings/2026-09.csv: the status column holds billed and void, never voided, so the skip test in the script matches nothing.
3. Read statement.py: the per-client aggregation and the printed format are fine; the skip test on `status == "voided"` is the fault.
4. Rewrite that one test (write_file or replace_lines) so that only rows whose status is billed are counted, leaving the log, the README and the printed format untouched; the fix lives in the code, so the logs added in later periods flow through it.

## Why the answer is unique
The decoy `TOTAL,10,210.00` is the sum over every row of both logs, and it is wrong because three of those rows are loads the firing room never charged: the studio writes a row when a load is booked, so a row in the log is not evidence of a charge, and README.md defines the statement as billed loads only. Nothing else in the data can move a figure: the only statuses are billed and void, every billed row carries a charge, and each charge is the same 875 pence per shelf, so the per-client split and the totals follow from the status column alone. With the October log present the statement is exactly:

    Bergamot Studio,3,52.50
    Corvid Ceramics,3,61.25
    Thistle and Fern,1,8.75
    TOTAL,7,122.50

Two other readings fail on their own terms rather than on taste. Marking the cancelled loads as billed by editing the log contradicts the record the studio keeps for the kiln room and fails the unchanged check on firings/2026-09.csv. Replacing the aggregation with the September figures alone ignores the logs later periods add, and the run covers those logs too.
