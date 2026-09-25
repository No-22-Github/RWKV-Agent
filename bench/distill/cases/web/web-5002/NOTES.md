## Traps
No traps. One search returns a single reference page and the table on it answers the question.

## Reference solution
1. Search for the Kelpforge ingest reference; the only result is docs.kelpforge.example/reference/ingest-tuning.
2. Open that page: the table gives flush_interval_ms as 250, with the default in the middle column, while flush_batch_size is 1000.

## Why the answer is unique
The page is Kelpforge's own reference for the ingest client and lists one default per setting. 1000 is the documented default of flush_batch_size, which bounds the size of a batch, not how long a partial batch waits; the question asks about the wait, and only the flush_interval_ms row states 250. The other numbers on the page (8 in flight, 2-second retry, 5 retries) are defaults of different settings.

## Five alternative phrasings of the task
Every query below carries the fixture keyword kelpforge, so each one is answered by the fixture entry.
1. kelpforge ingest flush interval default
2. kelpforge ingest tuning reference
3. kelpforge partial batch wait milliseconds
4. how long does the kelpforge client buffer a partial batch
5. kelpforge ingest client defaults table
