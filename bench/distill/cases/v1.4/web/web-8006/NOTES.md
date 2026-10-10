## Traps
- TR-WEBSTALE: a March 2026 trade article says removal "around mid-2027"; the official deprecations page (updated 2026-08-04) sets the /v1/batch sunset to 2026-12-01, after which requests return 410.

## Reference solution
1. Search Ostrander /v1/batch deprecation: the article and the official deprecations page.
2. Fetch https://docs.ostrander.com/deprecations.
Final answer, 1-2 sentences: /v1/batch is deprecated and stops working on 2026-12-01 (requests return 410 after that), per Ostrander's deprecation page; migrate to /v2/batch-jobs. Criteria: contains the date in any listed form, no "mid-2027", a fetch happened.

## Why the answer is unique
The official schedule is newer than the article and states an exact sunset date.

## Five alternative phrasings of the task
1. Ostrander /v1/batch deprecation
2. ostrander payments api v1 batch sunset
3. Ostrander API deprecations
4. ostrander batch endpoint removed
5. Ostrander v1 batch end of life
