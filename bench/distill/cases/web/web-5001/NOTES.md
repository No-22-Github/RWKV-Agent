## Traps
- TR-SUPERSEDE: docs.sablehook.example/guides/webhook-retry-schedule (guide updated 2025-10-08) is listed first by search and states up to 3 delivery attempts; docs.sablehook.example/reference/delivery-policy (revised 2026-08-19) states up to 6 and retires the older schedule. Answering from the first page gives 3.

## Reference solution
1. Search for "sablehook webhook delivery attempts": both fixture pages are returned, with the 2025 guide listed first.
2. Fetch docs.sablehook.example/reference/delivery-policy, revised 2026-08-19: "up to 6 delivery attempts for each event", and it states that the 3-attempt schedule published on 2025-10-08 no longer applies.
3. Answer 6.

## Why the answer is unique
Both pages are Sablehook's own documentation and each states its revision date in the body, so the two attempt counts are not competing claims from two sources: the 2026-08-19 page explicitly retires the 2025-10-08 schedule. The question asks for the count under the policy in force today (the harness clock reads 2026-09-16), and 3 is the count of a schedule the vendor has retired, so 3 cannot be the count in force. No third page in the fixture states an attempt count.

## Five alternative phrasings of the task
Every query below carries the fixture keyword sablehook, so each one is answered by a fixture entry.
1. sablehook webhook delivery attempts
2. sablehook webhook retry schedule
3. sablehook delivery policy attempt count
4. how many times does sablehook retry a webhook
5. sablehook webhook delivery policy reference
