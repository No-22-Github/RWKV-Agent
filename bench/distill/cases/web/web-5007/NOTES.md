## Traps
- TR-EARLYHIT: the first result, docs.otterbourne.example/errors/live, already gives the wait for OB-1130, so one search is enough; docs.otterbourne.example/errors/sandbox is a second page whose 5-second retry applies only in the sandbox and is the decoy.

## Reference solution
1. Search once for the Otterbourne error reference: the first result is the live error page, whose snippet gives the 90-second retry, and the sandbox page is listed with it.
2. Open docs.otterbourne.example/errors/live and confirm the OB-1130 row: retry the same request after 90 seconds; answer 90.

## Why the answer is unique
The two pages are labelled live and sandbox, and the question names the live API. The live page prescribes 90 seconds for OB-1130; the sandbox page states that its shortened timers are for testing, so its 5 seconds cannot be the wait for the live platform. 10 seconds belongs to OB-1002 and 1 second is the sandbox value for that code; neither is the wait for OB-1130 on the live API.

## Five alternative phrasings of the task
Every query below carries the fixture keyword otterbourne, so each one is answered by a fixture entry.
1. otterbourne OB-1130 retry seconds
2. otterbourne live error reference
3. otterbourne settlement window closed client action
4. otterbourne error code retry wait
5. otterbourne API errors reference
