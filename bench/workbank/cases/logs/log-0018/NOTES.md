## Traps
- TR-LONG: logs/fleetlens-ingest.log holds 388 records across the whole day (~40KB) and the
  requested record is a single FATAL line deep in the file. A reader who samples the start, or
  who takes the first ERROR-level record they meet, reports `rq-308957cf` (the shard-store
  ERROR at record 46 of 388, about 12% in); the FATAL record sits at record 259, two thirds of
  the way down, and its own call is `rq-c93f4485`.

## Reference solution
1. list_files to see the workspace layout; the ingest log is logs/fleetlens-ingest.log (1)
2. read_file README.md for the record grammar: the `call=` field names the ingress call and a
   FATAL record means the worker stopped (2)
3. Read the ingest log and locate the level field; INFO and WARN records fill most of the file,
   so search the level column (or the FATAL keyword) rather than reading from the top (3)
4. Report the call id carried by the one FATAL record, `rq-c93f4485` (4)

## Why the answer is unique
The log carries exactly one FATAL record (`... FATAL shard-store shard=... code=SHARD_CORRUPT
... call=rq-c93f4485`); every other record is INFO, WARN or ERROR, and each `call=` value is a
distinct ingress identifier, so `rq-c93f4485` appears on that line alone. The ERROR record near
the top (`code=BATCH_REJECTED`, call `rq-308957cf`) is the only other failure-grade record and is
the careless answer, but its level is ERROR, not FATAL, so it cannot be the requested record. The
scored answer is `rq-c93f4485`.
