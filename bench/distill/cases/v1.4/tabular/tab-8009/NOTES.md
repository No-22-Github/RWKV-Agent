## Traps
- TR-DATEFMT: the phone desk writes month/day/year (08/04/2026 is Aug 4). Reading those as day/month moves every such ticket out of the first two weeks of August, giving 23.

## Reference solution
1. data_query on support/tickets-2026-08.csv with filter {"queue": "billing"}, group_by opened, operation count.
2. Normalise each opened string to an August day using support/README.md (read once if needed); keep days 1-14 and add the counts with the calculator: 34.
Final answer, 1-2 sentences: 34 billing tickets were opened Aug 1-14; the opened column mixes four formats and the phone desk's 08/04/2026 style is month/day. Criteria: contains 34 as a whole token, data_query used, at most one read_file.

## Why the answer is unique
Every opened value parses to exactly one August day under the README's conventions; the queue filter is exact.
