## Traps
- TR-DECOY: settings/fallback.env 里留着 ERROR_RATIO_THRESHOLD=0.95 和 #oncall-eu，粗读会当成现行路由。 A careless pass reports `0.95`.

## Reference solution
1. List settings/ and read the README for which file wins.
2. Read settings/alerts.json for route, threshold and webhook.
3. Note that fallback.env is the retired EU pilot copy, then answer.

## Why the answer is unique
The README names alerts.json as authoritative and calls fallback.env a leftover, so 0.95 and #oncall-eu are retired; the live route is #oncall-apac with a 0.98 ratio threshold posting to the tessellar hook. alerts.json states each value once, so the reading is unique.
