# WORKBANK-CANARY-6b1f95d2 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

ticket = files["changes/CHG-2193.txt"]
match = re.search(r"max_connections in staging to (\d+)", ticket)
if not match:
    raise SystemExit("approved max_connections value not found in CHG-2193")
approved = match.group(1)

staging = files["environments/staging.env"]
updated = []
replaced = False
for line in staging.splitlines():
    if line.startswith("MAX_CONNECTIONS="):
        updated.append("MAX_CONNECTIONS=" + approved)
        replaced = True
    else:
        updated.append(line)
if not replaced:
    raise SystemExit("MAX_CONNECTIONS line not found in staging env file")
print(json.dumps({"files": {"environments/staging.env": "\n".join(updated) + "\n"}}))
