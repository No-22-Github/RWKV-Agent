## Traps
- TR-EARLYHIT: the first result is the CDN's error reference and its snippet states the
  16 hop ceiling, so one search is enough and the case caps web_search at 1.
  docs.ashcott.example/limits/edge-rules is the decoy: its 8 hops counts handovers inside
  an edge rule, which the page says are counted separately from browser redirects.

## Reference solution
1. Search once for the Ashcott AC-4210 reference: the first result is the error page with
   the hop ceiling in its snippet, and the edge rule limits page is listed beside it.
2. Open docs.ashcott.example/errors/redirect-loop and read the AC-4210 row: a request
   that follows more than 16 redirect hops ends on that error.

## Why the answer is unique
The error page names the code the storefront ends on and attaches one ceiling to it, with
a worked example: sixteen redirects are served and the seventeenth is refused. The edge
rule page counts a different kind of hop and states that browser redirects are counted
separately, so its 8 cannot be the ceiling AC-4210 is raised at. AC-4204 and AC-4288
describe other faults.

## Five alternative phrasings of the task
1. ashcott AC-4210 redirect hops
2. ashcott redirect error reference
3. how many redirects before ashcott raises AC-4210
4. ashcott cdn redirect loop error
5. ashcott error codes redirect ceiling
