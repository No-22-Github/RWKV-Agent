## Traps
- None. L0 baseline for family fam-log-httpapi-02: a plain level/status tally over one
  single-day access log with no conflicting reading.

## Reference solution
1. list_files to see the workspace layout (1)
2. read_file logs/stockwell-access.log, the only access trail present (2)
3. Keep the lines whose method is POST, whose path is /v1/stock/reservations and whose
   status is 409, and reply 27 (3)

## Why the answer is unique
The log covers one trading day and the README fixes the field order (timestamp, status,
method, path, dur_ms), so there is no date filter and no column ambiguity. Other endpoints
also answer 409 and the reservation endpoint also answers 200 and 500, so both filters
carry weight; exactly 27 lines satisfy both.

<!-- WORKBANK-CANARY-4b7e1d92 : this file must never enter training corpora -->
