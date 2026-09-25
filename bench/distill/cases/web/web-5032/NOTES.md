## Traps
- TR-EARLYHIT: the first result is Yarnbrook's collector reference and its snippet gives
  the read timeout (26 seconds), so one search is enough and the case caps web_search
  at 1. The 45 seconds on the field kit page is the decoy: that page says the field kit
  is a separate build whose timings do not apply to the standard collector.

## Reference solution
1. Search for the Yarnbrook collector defaults: the reference page is the first result
   and its snippet carries the timeout, with the field kit page beside it.
2. Open docs.yarnbrook.example/reference/collector-defaults and read the
   read_timeout_seconds row: the collector waits 26 seconds for a reading before it
   marks the device unreachable.

## Why the answer is unique
The page pairs the setting with its job: read_timeout_seconds is the wait for a
reading, and the page says a silent device is dropped after exactly that. The 15
seconds beside it is the flush interval, which governs when readings are handed to
the ingest API rather than how long the collector waits. The field kit page's 45
seconds belongs to a separate build of the collector.

## Five alternative phrasings of the task
1. yarnbrook collector defaults
2. yarnbrook read timeout seconds
3. how long does the yarnbrook collector wait for a reading
4. yarnbrook telemetry collector reference
5. yarnbrook field kit timings
