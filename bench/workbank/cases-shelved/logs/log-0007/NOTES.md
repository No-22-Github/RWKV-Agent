## Traps
- TR-TRUNC: logs/tessellate-access.log is 77867 bytes, so a single pass over the trail
  stops around 13:51 and never reaches the cutover marker at 13:52:06 or the failed quote
  request at 13:52:17 that answers the question. The head does hold 57 quote failures from
  the 11:41-12:12 burst, so reading it and taking the first failed quote request gives the
  decoy 3390 instead of 6014.

## Reference solution
1. list_files to see the workspace layout (1)
2. read_file README.md, which fixes the field order and says a 5xx answer is a failed request (2)
3. read_file logs/tessellate-access.log; the head ends before the cutover, so continue past it
   (a second pass with an offset, or a search for the cutover marker) (3)
4. Take the first quote request after the 13:52:06 cutover line whose status is 5xx and
   report its dur_ms: 6014 (4)

## Why the answer is unique
The README defines failure as a 5xx answer, so the burst entries and the post-cutover
failures fall under one definition. The cutover marker is the only line naming the move to
ratesvc-2, and the request immediately after it is the only quote request in the file
stamped between 13:52:06 and 13:52:17, so "first failure after the move" selects exactly one
line. The decoy 3390 belongs to a request at 11:41:18, two hours and eleven minutes earlier, and the burst cannot be read
as post-cutover: every burst timestamp is below the marker's.

<!-- WORKBANK-CANARY-6d2e8b47 : this file must never enter training corpora -->
