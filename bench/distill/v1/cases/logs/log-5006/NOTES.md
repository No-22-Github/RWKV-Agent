## Traps
- TR-DECOY: logs/gateway.jsonl also holds /v2/ledger/export records, and their `route` value starts with the route in the question. Summing the `bytes` of every record whose route merely starts with /v2/ledger gives 171443 instead of 119202. The export route is documented in README.md as its own route, which streams a month of postings in one response.

## Reference solution
1. List the workspace: README.md and logs/gateway.jsonl.
2. Read README.md: one record per request, `bytes` is the response body size, and /v2/ledger/export is a separate route from /v2/ledger.
3. Read logs/gateway.jsonl (or filter it by `route` = /v2/ledger and sum `bytes`). The 19 records for that route sum to 119202.

## Why the answer is unique
The question names one route, and README.md lists the four routes the gateway serves, so /v2/ledger and /v2/ledger/export are different routes. The 19 records whose `route` is exactly /v2/ledger carry 119202 bytes in total. The decoy 171443 comes from letting the seven export records into the sum; those are responses to a different route and are not part of what the question asks for. Summing the whole file (199689) answers a third question. With the route taken literally, the answer is 119202.

## Fixture notes
`bytes` is a bare integer in every record so the field can be summed directly, and no other field in the record carries the response size. The file holds 42 records for 7 August 2026 and every record's `ts` is on that day, so no date filtering is needed.
