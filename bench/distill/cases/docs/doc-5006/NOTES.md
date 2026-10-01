## Traps
- TR-ABSENT: the schedule in fees/schedule-2026.csv prices site collections but never a Saturday collection, and collections.md says collections are made on working days only. Stopping at the first collection row gives the decoy 28.00, the fee for a collection at the customer site.

## Reference solution
1. List the workspace, then read fees/schedule-2026.csv and collections.md.
2. fees/schedule-2026.csv prices three kinds of collection, all of them working-day services by their turnarounds, and lists no Saturday collection; collections.md states collections are made on working days only, so the laboratory offers nothing on a Saturday and no fee for a Saturday collection exists in the folder.
3. Final answer in two or three sentences: name the files checked, say there is no Saturday collection in the 2026 schedule and so no fee for one, and point to the nearest row (a collection at the customer site) as a different service without quoting its figure. Scored with output_contains_any over "Saturday collection", "saturday collection", "collection on a Saturday" or "Saturday service"; output_excludes rules out UNKNOWN and the 28.00 site-collection fee, so the reply names the missing service instead of quoting any fee.

## Why the answer is unique
The decoy 28.00 is wrong because that row prices a collection at the customer site, and collections.md restricts every collection the laboratory runs to working days, so the row cannot be applied to a Saturday without contradicting the note. The set contains no Saturday service and no weekend rate, so the only truthful reply is the one that reports the absence: fees/schedule-2026.csv and collections.md were checked, no Saturday collection is listed in either, and the nearest row — a collection at the customer site — is a different service whose fee is not the answer to the question.
