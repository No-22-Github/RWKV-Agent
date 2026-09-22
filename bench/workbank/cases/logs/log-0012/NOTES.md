## Traps
- TR-TZ: logs/edge-proxy.log is stamped in UTC (trailing Z) while logs/session-store.log carries `+08:00`, and the prompt asks for the instant in Singapore time. The onset falls in the proxy log, so a reader who does not convert reports `2026-09-28 09:30:58` (the correct instant with the wrong zone); a reader who converts the store lines but not the proxy line lands on a different value entirely.
- TR-MULTISRC: the onset is not the first line of either log. The store log's own first ERROR (`AUTH_FAIL`) is at 17:31:14+08:00, sixteen seconds after the outage already showed a failure in the proxy, so a store-only reader reports `2026-09-28 17:31:14`; a proxy-only reader who takes the earliest 502 in that file is pulled onto the unrelated `search-service` failure at 08:12:30Z. Only placing both logs on one timeline gives the true onset.

## Reference solution
1. list_files to see the two service logs (1)
2. read_file README.md for which log uses which offset and the shared request id (2)
3. read_file logs/edge-proxy.log and collect the session-store 502 lines with their Z timestamps (3)
4. read_file logs/session-store.log and collect the AUTH_FAIL lines with their +08:00 timestamps (4)
5. Put both on one timeline, take the earliest failure of the outage (2026-09-28T09:30:58Z) and report it in the requested zone as `2026-09-28 17:30:58` (5)

## Why the answer is unique
The outage is the session path: every session-store 502 in the proxy log carries `upstream=session-store`, and every store AUTH_FAIL carries `reason=redis_auth_error`. On one timeline the earliest such failure is the proxy line at 09:30:58Z = 17:30:58+08:00; the store's first AUTH_FAIL is 16 seconds later at 17:31:14+08:00. The proxy's other 502 (08:12:30Z) is `upstream=search-service` and belongs to a different service and incident - reporting it in the requested zone gives `2026-09-28 16:12:30`, a derivable wrong answer that is not a registered decoy - and the store's SLOW_QUERY burst is a P3 scan-latency event that its own `recovered` line closes at 15:52:07+08:00, well before the outage. With the onset pinned to the earliest session failure and the requested zone fixed by the prompt, the answer is `2026-09-28 17:30:58`.
