## Traps
- TR-MULTISRC: the edge symptom is in logs/api-gateway.log and the fault code is in logs/order-service.log, and the two only line up once their timelines are placed together. Read alone, the gateway shows only `reason=upstream_timeout` (plus an unrelated earlier 502 to search-service), so a gateway-only reader reports UPSTREAM_TIMEOUT or blames search-service; read alone, the order-service log offers two separate bursts and the earlier one is `CART_LOCK_TIMEOUT` (four records at 08:41:09-08:53:18, against five PG_CONN_RESET records at 09:14:23-09:41:53), so a backend-only reader who takes the first burst reports CART_LOCK_TIMEOUT. The gateway's first order-service 502 lands at 09:14:22, which is 21 minutes after the CART_LOCK_TIMEOUT burst ended and one second before the `PG_CONN_RESET` burst begins; the merged timeline therefore names PG_CONN_RESET.

## Reference solution
1. list_files to see the two service logs (1)
2. read_file logs/api-gateway.log and note the first order-service 502 at 09:14:22 (2)
3. read_file logs/order-service.log and read the JSON-lines records with their UTC ts values (3)
4. Align the order-service error bursts to the gateway onset and report the code of the first backend ERROR at or after 09:14:22, which is `PG_CONN_RESET` (09:14:23) (4)

## Why the answer is unique
The gateway's order-service 502 onset is single-valued at 09:14:22. In the order-service log the two ERROR bursts are separated by a recovery marker: CART_LOCK_TIMEOUT runs 08:41:09-08:53:18 and `lock_recovered` at 08:58:02 closes it, while PG_CONN_RESET runs 09:14:23-09:41:53. Only PG_CONN_RESET lies at or after the gateway onset, and every PG_CONN_RESET record carries the same request id as a gateway 502 line, so the pairing is exact rather than inferred. The CART_LOCK_TIMEOUT burst cannot be the fault behind this wave because it had recovered half an hour before the first edge 502, so the answer is `PG_CONN_RESET`.
