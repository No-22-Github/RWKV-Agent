# WORKBANK-CANARY-7d21b4ea : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
files = case["files"]

order = files["changes/WO-5580.txt"]
match = re.search(r"max_batch_records to (\d+)", order)
if not match:
    raise SystemExit("WO-5580 does not state the new max_batch_records value")
new_value = match.group(1)

target = "services/spool-writer.yaml"
updated = []
replaced = False
for line in files[target].split("\n"):
    if re.match(r"\s*max_batch_records:", line) and not replaced:
        new_line = re.sub(r"(max_batch_records:\s*)\d+", r"\g<1>" + new_value, line)
        if new_line == line:
            raise SystemExit("max_batch_records value not replaced")
        updated.append(new_line)
        replaced = True
    else:
        updated.append(line)
if not replaced:
    raise SystemExit("max_batch_records not found in services/spool-writer.yaml")

print(json.dumps({"files": {target: "\n".join(updated)}}))
