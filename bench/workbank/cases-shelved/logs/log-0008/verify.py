# WORKBANK-CANARY-c9037af6 : bank artifact, excluded from training corpora
"""Expected answer for log-0008: 503 answers to POST /v2/inspection/submit after the reload.

The reload marker is the first line of the log; the refused submits for the inspection
endpoint run from 07:31:36 to 10:54:22, and most of them sit past the point a single pass
over the log's head reaches.
"""
import json

case = json.load(open("case.json"))
log = case["files"]["logs/foundry-api.log"]
lines = [ln for ln in log.splitlines() if ln.strip()]

marker = lines[0]
if "config reload applied" not in marker:
    raise SystemExit("reload marker is not the first line of foundry-api.log")
cut = marker.split()[0]

count = 0
for ln in lines[1:]:
    parts = ln.split()
    # <ts> <status> <method> <path> ... for access lines; level lines carry a word status
    if len(parts) < 4 or parts[0] <= cut:
        continue
    if parts[1] == "503" and parts[2] == "POST" and parts[3] == "/v2/inspection/submit":
        count += 1
print(json.dumps({"expected_number": count}))
