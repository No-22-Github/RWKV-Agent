## Traps
- TR-EARLYHIT: the first result is Silverdale's own notice for the v2 feed and its
  snippet states the ceiling (55 calls per minute), so one search is enough and the
  case caps web_search at 1. The v3 reference is the decoy: its 300 calls per minute
  applies to the feed the tracker is moving to, not the one it still polls.

## Reference solution
1. Search for the Silverdale tracking v2 notice: it is the first result and its snippet
   carries the ceiling, with the v3 reference beside it.
2. Open silverdale.example/notices/tracking-v2: while the notice runs the feed is held
   to 55 calls per minute for each account and calls past that ceiling are refused.

## Why the answer is unique
The notice names the feed it covers and attaches one ceiling to it, and it says the
feed still answers during the notice period, so the ceiling is in force for the
tracker that keeps polling v2. SD-429 is the code a call past the ceiling is refused
with rather than a call allowance. The 300 calls per minute on the v3 page belongs to
the replacement feed, which the notice describes as a different feed.

## Five alternative phrasings of the task
1. silverdale tracking v2 notice
2. silverdale v2 tracking feed calls per minute
3. when does silverdale switch off the v2 tracking feed
4. silverdale tracking v3 reference
5. silverdale freight SD-429 refusal
