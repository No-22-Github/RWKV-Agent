## Traps
- The sandbox has no curl and no network; `curl https://status.ferrowave.net/api/summary.json` fails with command not found. The page is reachable through the web fetch tool.

## Reference solution
1. bash: `curl -s https://status.ferrowave.net/api/summary.json` -> command not found (optional; the recovery is the point)
2. web_fetch https://status.ferrowave.net/api/summary.json
Final answer: ap-east has a partial outage according to Ferrowave's status summary (updated 2026-09-16 02:10 UTC); eu-west and us-east are operational. curl isn't available in the sandbox, so I fetched the page with the web tool.

## Why the answer is unique
The page states one value.

## Five alternative phrasings of the task
1. Which Ferrowave region is down right now?
2. Check the Ferrowave status JSON for any outage.
3. Is our CDN healthy in every region?
4. Fetch the Ferrowave status summary and name the bad region.
5. Any partial outage on Ferrowave at the moment?
