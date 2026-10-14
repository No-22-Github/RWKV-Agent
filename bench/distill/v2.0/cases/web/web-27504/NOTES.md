## Traps
- TR-EARLYHIT: the vendor deprecation schedule ranks first and its snippet
  already names the removal version; expect.max_calls budgets a single
  web_search call. The v9 cutover post ranked second talks about sandbox
  retirement and can mislead a search that goes on too long (decoy 9).

## Reference solution
1. web_search larkspur mail api deprecation schedule (1)
2. Answer 11 from the schedule snippet (2)

## Why the answer is unique
The vendor's deprecation schedule states the legacy /v1/aliases endpoint will
be removed in API version 11. The v9 cutover blog describes retiring the old
alias handling on sandbox clusters - deprecation of the handling, not the
removal version of the endpoint - so 9 is not a supportable answer and 11 is
the only removal version the vendor page gives for /v1/aliases.

## Five alternative phrasings of the task
1. larkspur mail api deprecation schedule aliases
2. larkspur v1 aliases endpoint removed version
3. which larkspur api version removes v1 aliases
4. larkspur mail api legacy endpoints sunset
5. larkspur developers deprecations v1 aliases
