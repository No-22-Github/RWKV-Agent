# WORKBANK-CANARY-51c07af3 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

request = files["changes/CR-8842.txt"]
match = re.search(r"TENANT_CALL_QUOTA to (\d+)", request)
if not match:
    raise SystemExit("CR-8842 does not state the new TENANT_CALL_QUOTA value")
new_value = match.group(1)

target = "environments/staging.env"
updated = []
replaced = False
for line in files[target].split("\n"):
    if line.startswith("TENANT_CALL_QUOTA=") and not replaced:
        updated.append("TENANT_CALL_QUOTA=" + new_value)
        replaced = True
    else:
        updated.append(line)
if not replaced:
    raise SystemExit("TENANT_CALL_QUOTA not found in environments/staging.env")

print(json.dumps({"files": {target: "\n".join(updated)}}))
