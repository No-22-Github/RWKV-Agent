## Traps
- TR-DUPROW: the retry wrote four in-scope contracts twice, so counting matched rows gives 24. The README says rental_id identifies the contract, so the answer is the number of different renters, 19.

## Reference solution
1. read_file README.md: retry may repeat a contract row; renter_id identifies the customer.
2. data_query: {"path":"data/equipment_log.csv","filter":{"rental_month":"2026-01","gear_class":"Snowboard Package"},"operation":"distinct_count","field":"renter_id"} -> 19.
3. Reply with the number 19 only.

## Why the answer is unique
The decoy 24 counts rows, but the task asks how many different customers rented, and the README states the retry wrote contracts twice, so repeated rows are the same rental seen twice. Every repeated row matches its original in every column, so there is no reading in which they are separate customers. December and February rows fail the month condition. The answer is 19.
