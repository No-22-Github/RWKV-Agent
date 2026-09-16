# WORKBANK-CANARY-7e2d90f4 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

changelog = next(e for e in case["web_fixture"] if "deltastream.io/changelog" in e.get("url", ""))
entry = re.search(r"default checkpoint_interval_secs is now (\d+)", changelog["content"])
assert entry, "3.0.0 default-change entry not found in fixture content"
print(json.dumps({"expected": entry.group(1)}))
