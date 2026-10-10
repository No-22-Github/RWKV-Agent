## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): the prompt asks for people, and the log has no column named person or recipient - only the near-name pair recv_id (the person) and recv_dept (the shared mail stop). A distinct_count over a guessed column first fails with `field "..." is missing`; a wrong column inside filter returns matched_rows 0. The model must recover: list the real columns with a select query (no operation), or peek at the header with the single read_file the case budget allows, then re-query with recv_id. The README pins the mapping: recv_id is the person, recv_dept is only the mail stop.
- Counting mail stops instead gives 6; the correct answer, the distinct people, is 23.

## Reference solution
1. read_file README.md: recv_id identifies the person; several people share a recv_dept mail stop.
2. data_query: {"path":"data/parcel_intake.csv","filter":{"intake_month":"2026-05","carrier":"RapidShip"},"operation":"distinct_count","field":"recv_id"} -> 23. (If the first attempt guessed a column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 23 only.

## Why the answer is unique
The decoy 6 counts mail stops, but the task asks how many different people received parcels, and the README states several people share one mail stop, so the stop count cannot answer a people count. April and June rows, and other couriers, fail the filter. The answer is 23.
