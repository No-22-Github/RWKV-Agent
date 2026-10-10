## Traps
- TR-HEADER: exports/pump-outs-may.csv ends with a TOTAL line reading "10 services". It counts every row including the two void bookings, so quoting it answers the completed-pump-outs question with 10 instead of 8.

## Reference solution
1. Read README.md: void bookings were cancelled before the boat tied up and only done services are billable; the TOTAL line counts every row.
2. Read exports/pump-outs-may.csv.
3. Keep status=done rows: 8 pump-outs; berth counts among done rows put A2 first with 4; void rows number 2.

## Why the answer is unique
The decoy 10 services is the file's own TOTAL line. README states that line counts every row regardless of status, and the two void rows (PO-2203, PO-2207) are bookings cancelled with the boat never tied up, so they are not completed services under the file's own rule; the completed count can only be 8. Among done rows A2 appears 4 times against A5's 3, so the busiest berth is A2, and exactly 2 rows carry status void. A summary that answers the three questions from the file's own status rule lands on those three facts and no other reading exists.
