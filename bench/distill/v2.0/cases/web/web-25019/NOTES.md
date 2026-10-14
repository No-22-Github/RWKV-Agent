## Traps
- TR-EARLYHIT: the first result is the broker's own lease reference and its snippet
  states the 900 second standard lease, so one search is enough and the case caps
  web_search at 1. docs.landwick.example/start/first-consumer is the decoy: its 120
  second lease belongs to a guided exercise.

## Reference solution
1. Search once for the Landwick lease reference: the first result is the reference page
   with the 900 second standard lease in its snippet, and the walkthrough is listed
   beside it.
2. Open docs.landwick.example/reference/leases and read the table: lease_seconds is 900
   by default.

## Why the answer is unique
The reference page is the broker's own table of what each setting does when it is left
alone, and the question describes a worker that leaves the settings alone, so 900
applies. The walkthrough states its 120 second lease as an exercise setting and says a
real consumer takes the standard lease. The other numbers on the reference page, 30 and
6, are the prefetch depth and the redelivery limit.

## Five alternative phrasings of the task
1. landwick queue lease reference
2. landwick lease_seconds default
3. how long before a landwick message returns to the queue
4. landwick broker unacknowledged message wait
5. landwick queue default settings
