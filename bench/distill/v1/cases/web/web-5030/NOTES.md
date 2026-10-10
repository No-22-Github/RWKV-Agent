## Traps
- TR-EARLYHIT: the first result is Hallowbrook's error reference and its snippet states
  the body ceiling (128 kilobytes), so one search is enough and the case caps
  web_search at 1. The edge buffering note is the decoy: its 96 kilobytes is how much
  the edge holds before streaming, and that page says the buffer does not change the
  size a request may carry.

## Reference solution
1. Search for the Hallowbrook ingest errors: the error page is the first result and
   its snippet carries the ceiling, with the edge buffering page beside it.
2. Open docs.hallowbrook.example/errors/ingest and read the HB-5510 row: a single
   request body that goes past 128 kilobytes ends on that code.

## Why the answer is unique
The code the sender keeps ending on has one condition attached to it, and the page
spells out the boundary: exactly 128 kilobytes is accepted and the next kilobyte ends
on HB-5510. HB-5502 and HB-5533 describe other faults, and the 96 kilobytes on the
buffering page is an internal buffer size that the page says leaves the permitted
body size alone.

## Five alternative phrasings of the task
1. hallowbrook ingest errors
2. hallowbrook HB-5510 meaning
3. hallowbrook request body size limit
4. how large a body before hallowbrook raises HB-5510
5. hallowbrook edge buffering kilobytes
