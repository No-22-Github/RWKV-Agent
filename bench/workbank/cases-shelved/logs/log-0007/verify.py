# WORKBANK-CANARY-6d2e8b47 : bank artifact, excluded from training corpora
"""Expected answer for log-0007: dur_ms of the first failed quote request after the cutover.

The cutover marker and the first failed quote request after it both sit past the point a
single pass over the trail's head reaches; the earlier burst in the head is a different
incident.
"""
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/tessellate-access.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

cut = None
for ln in lines:
    if "cutover" in ln and "ratesvc-2" in ln:
        cut = ln.split()[0]
        break
if cut is None:
    raise SystemExit("cutover marker not found in tessellate-access.log")

for ln in lines:
    parts = ln.split()
    if len(parts) < 4 or parts[0] <= cut:
        continue
    if parts[1] == "GET" and parts[2] == "/api/v3/shipments/quote" and parts[3].startswith("5"):
        m = re.search(r"dur_ms=(\d+)", ln)
        if not m:
            raise SystemExit("failed quote request carries no dur_ms field: %s" % ln)
        print(json.dumps({"expected_number": int(m.group(1))}))
        break
else:
    raise SystemExit("no failed quote request found after the cutover")
