# WORKBANK-CANARY-3f8ac620 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

request = files["changes/CR-2071.txt"]
match = re.search(r"MAX_UPLOAD_MB to (\d+)", request)
if not match:
    raise SystemExit("CR-2071 does not state the new MAX_UPLOAD_MB value")
new_value = match.group(1)

target = "environments/staging.env"
updated = []
replaced = False
for line in files[target].split("\n"):
    if line.startswith("MAX_UPLOAD_MB=") and not replaced:
        updated.append("MAX_UPLOAD_MB=" + new_value)
        replaced = True
    else:
        updated.append(line)
if not replaced:
    raise SystemExit("MAX_UPLOAD_MB not found in environments/staging.env")

print(json.dumps({"files": {target: "\n".join(updated)}}))
