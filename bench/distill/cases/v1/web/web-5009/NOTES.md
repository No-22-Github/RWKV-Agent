## Traps
- TR-EARLYHIT: the first result, quillstone.example/migrations/v1-orders, already states the orders window, so one search is enough; quillstone.example/migrations/v1-shipments is a second notice whose 365-day window applies to the shipments endpoints and is the decoy.

## Reference solution
1. Search once for the Quillstone retirement notices: the first result is the v1 orders notice, whose snippet gives the 120-day window, and the shipments notice is listed with it.
2. Open quillstone.example/migrations/v1-orders and confirm the 120-day window; answer 120.

## Why the answer is unique
Each notice covers the endpoints named in its title, and the question names the v1 orders endpoints. The orders notice states 120 days and the shipments notice states 365 days for its own endpoints, so 365 cannot be the orders window. 410 is the status returned once a window has closed, not a window length.

## Five alternative phrasings of the task
Every query below carries the fixture keyword quillstone, so each one is answered by a fixture entry.
1. quillstone v1 orders retirement notice
2. quillstone orders endpoints deprecation window
3. quillstone v1 orders days before removal
4. how long do quillstone v1 orders endpoints keep working
5. quillstone migration notices
