## Traps
- TR-DUPROW: the flow logger re-sent 5 egress_flush events unchanged (same event_id), so the journal holds 23 flush lines over 18 distinct events. Summing lines answers the overshoot; merging by event_id and summing bytes_out once per event gives 23766823.

## Reference solution
1. Read README.md: the JSONL record shapes and the re-send rule.
2. Search 'egress_flush' and read the lines around the hits.
3. Keep the first occurrence of each event_id, take its bytes_out.
4. The total is 18739843.

## Why the answer is unique
Re-sent events repeat every field including event_id, so the README's count-once rule makes them one event; other kinds are excluded by kind. The deduplicated total is 18739843 bytes_out.
