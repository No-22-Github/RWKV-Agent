## Traps
- TR-MULTISRC: the incident window exists only in logs/parcel-router.log (rate-sheet sync markers: rev 8842 rejected 13:07:22, rev 8847 accepted 15:31:40); the failure records exist only in the fulfillment-gw logs. Router alone counts 11 Meridian quote rejections (three of them ended as route_cancelled, not failed attempts); gateway alone counts 12 FF_ROUTE_FAIL records. Both single-source readings are wrong; the answer is the 8 gateway failures inside the router-derived window.
- TR-DECOY: the same FF_ROUTE_FAIL code also appears in the morning Kestrel quota blip (three records in fulfillment-gw.log.1, paired with the PR_RATE_LIMIT lines) and once after recovery (15:52:10, BlueCrane peer timeout), so counting all failures by code gives 12 instead of 8.

## Reference solution
1. list_files (1)
2. read_file README.md for the field and event glossary (2)
3. read_file logs/parcel-router.log: find the rate-sheet markers (rejected 13:07:22, accepted 15:31:40) and the 11 Meridian rejections (3)
4. read_file logs/fulfillment-gw.log (4)
5. read_file logs/fulfillment-gw.log.1, keep FF_ROUTE_FAIL records inside the window, reply 8 (5)

## Why the answer is unique
The glossary defines FF_ROUTE_FAIL as a failed fulfillment attempt and route_cancelled as no attempt created, so the attempt count is the FF_ROUTE_FAIL count. The window is pinned by two marker lines with wide margins: the nearest in-window failure is 13:09:15 (about two minutes after the start marker) and the nearest out-of-window failure is 15:52:10 (over 20 minutes after the end marker). Every in-window failure trails a Meridian rejection by 1-4 seconds and every rejection pairs with exactly one gateway record (8 failures, 3 cancellations), so no reading of the pairing changes the total.

<!-- WORKBANK-CANARY-d18a04f3 : this file must never enter training corpora -->
