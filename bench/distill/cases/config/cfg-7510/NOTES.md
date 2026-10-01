## Traps
- TR-DECOY: conf/enrich.flags 与 conf/ingest.flags 的 batch_rows 同为 512，粗读会把它当成差异项。 A careless pass reports `512`.

## Reference solution
1. Read conf/enrich.flags and conf/ingest.flags key by key.
2. Note that batch_rows matches at 512 while mode and sink differ.
3. Check conf/sink-map.list for what each sink table holds, then summarize.

## Why the answer is unique
mode is stream for enrich and batch for ingest, and the sinks point at events_enriched versus events_raw, while batch_rows is 512 in both files, so the only differences are mode and sink. sink-map.list confirms the two tables are distinct tiers of the same pipeline, leaving no third reading.
