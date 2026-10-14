## Traps
- TR-TRUNC: the log is about 110 KB, beyond read_file's 64 KiB, so a single read stops before line 912.
- TR-DECOY: line 403 is a WARN about a checksum retry, not a mismatch.

## Reference solution
1. search_text for "checksum mismatch" in logs/sync-worker.log: matches at lines 912, 1205 and 1378.
Final answer, one sentence: the first checksum mismatch is on line 912 and involves warehouse/exports/sku-feed-0915.parquet. Criteria: contains 912 (whole token) and the file path; at most one read_file.

## Why the answer is unique
"checksum mismatch" first appears on that line; the earlier checksum line is a retry WARN.
