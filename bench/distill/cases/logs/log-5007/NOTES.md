## Traps
- TR-DEFN: every record carries two similar size fields. `bytes_in` counts what the producers handed the router and `bytes_out` counts what the router passed to the destination mailboxes, so totalling the field that reads first (bytes_in) gives 5002220 instead of 4839980. README.md defines both fields; the question asks for the destination side.

## Reference solution
1. List the workspace: README.md and logs/router.jsonl.
2. Read README.md: one record per batch, `bytes_in` is the producer side and `bytes_out` is what the router passed on to the destination mailboxes.
3. Read logs/router.jsonl (or aggregate `bytes_out` over the file). The 44 batch records sum to 4839980.

## Why the answer is unique
The question asks for the volume that reached the destination mailboxes, and README.md assigns that meaning to exactly one field. Summing `bytes_in` gives 5002220, which is the volume the producers handed over, not the volume the destinations received; the difference is the re-encoding the router does on each batch. `msgs` counts messages rather than bytes, so it cannot answer the question either. Summing the field the question names gives 4839980.

## Fixture notes
Both size fields are bare integers on every record, so either can be aggregated directly. The journal covers one run on 8 August 2026, with batches for three queues and no record carrying a run total, so no record has to be excluded from the sum.
