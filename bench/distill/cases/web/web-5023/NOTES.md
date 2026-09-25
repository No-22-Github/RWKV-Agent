## Traps
- TR-EARLYHIT: the first result is the relay's own queue reference and its snippet gives
  the 400 message batch, so one search is enough and the case caps web_search at 1.
  docs.cobbleyard.example/plans/entry is the decoy: its 50 message batch belongs to the
  entry plan, which caps the daily count.

## Reference solution
1. Search once for the Cobbleyard delivery queue reference: the first result is the
   reference page with the 400 message batch in its snippet, and the entry plan page is
   listed beside it.
2. Open docs.cobbleyard.example/reference/delivery-queue and read the table:
   batch_messages is 400 by default.

## Why the answer is unique
The reference page states the default for a relay and says the volume plans that cap the
daily count set their own figure, so the figure for a full relay is 400. The entry plan
page accounts for 50 on its own and says the larger plans take the relay default. The
remaining numbers, 30 and 4, are the drain interval and the retry window.

## Five alternative phrasings of the task
1. cobbleyard delivery queue reference batch size
2. cobbleyard outbound queue drain batch
3. how many messages per cobbleyard drain
4. cobbleyard relay queue defaults
5. cobbleyard mail relay batch_messages default
