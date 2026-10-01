## Traps
- TR-DUPROW: logs/edge-access.log repeats req-6115, req-6128 and req-6151 verbatim (the export job retried). Counting rows gives 17; the README says the request id uniquely identifies a request, so the answer is 14 distinct requests.

## Reference solution
1. Turn 1: read README.md (the export retried; request id identifies a request), read logs/edge-access.log, collect request ids with status 5xx: 14 distinct (17 rows). Answer: 14 笔.
2. Turn 2: rescope to /checkout: req-6102, 6107, 6115, 6128, 6134, 6151 = 6 distinct. Answer: 6 笔.
3. Turn 3: drop client IPs starting with 10.42. (load-test rig): 6102, 6115, 6134, 6151 = 4. Answer: 4 笔.

## Why the answer is unique
The decoy 17 counts rows, but repeated rows are byte-identical and share one request id, and the README states the id uniquely identifies a request, so the repeated lines are one request written several times. Every 5xx row carries one of the 14 ids, and no id appears with two different statuses or paths, so there is no reading under which the count is anything but 14 (6 for /checkout, 4 after excluding 10.42.*).
