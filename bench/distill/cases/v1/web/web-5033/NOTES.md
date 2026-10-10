## Traps
- TR-EARLYHIT: the first result is Stanmere's own error reference and its snippet gives
  the wait for SM-4402 (37 seconds), so one search is enough and the case caps
  web_search at 1. The key lock page is the decoy: its 12 seconds belongs to SM-4409
  and that page says the two codes never share a figure.

## Reference solution
1. Search for the Stanmere rate window errors: the error page is the first result and
   its snippet carries the wait, with the key locks page beside it.
2. Open support.stanmere.example/errors/rate-window and read the SM-4402 row: the
   reply asks the caller to wait 37 seconds, and the page says a caller that waits that
   time gets through.

## Why the answer is unique
The code the night batch keeps ending on has one reply attached to it, and the page
adds that the wait is fixed for the endpoint rather than growing with repeats, so the
figure does not drift. SM-4401 is refused outright and carries no wait, and the 12
seconds on the other page is the release time for a key held under SM-4409, which the
page states is a separate mechanism.

## Five alternative phrasings of the task
1. stanmere rate window errors
2. stanmere SM-4402 wait seconds
3. how long to wait after stanmere SM-4402
4. stanmere token bucket error reference
5. stanmere SM-4409 key locks
