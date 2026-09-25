## Traps
- TR-EARLYHIT: the first result is the error reference for the live platform and its
  snippet already gives the 25 second retry, so one search is enough and the case caps
  web_search at 1. docs.sheldwich.example/errors/trial is a second page whose 3 second
  timer applies to trial accounts and is the decoy.

## Reference solution
1. Search once for the Sheldwich SH-4410 reference: the first result is the live error
   page, whose snippet gives the 25 second retry, with the trial page listed beside it.
2. Open docs.sheldwich.example/errors/current and read the SH-4410 row: retry the same
   request after 25 seconds.

## Why the answer is unique
The two pages are labelled live and trial, and the question names the live platform, so
the live reference governs. It prescribes 25 seconds for SH-4410; the trial page states
that its shortened timers are for integrations being built, so its 3 seconds cannot be
the wait for a settlement worker on the live platform. SH-4402 and SH-4477 carry
different meanings and neither names a wait.

## Five alternative phrasings of the task
1. sheldwich SH-4410 retry seconds
2. sheldwich current error reference
3. sheldwich duplicate settlement request client action
4. sheldwich payment error retry wait
5. sheldwich live errors reference
