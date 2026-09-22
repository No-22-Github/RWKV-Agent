# WORKBANK-CANARY-2f8a6d05 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

releases = next(e for e in case["web_fixture"] if "threadneedle.io/releases" in e.get("url", ""))
entry = re.search(r"current stable threadneedle release is ([0-9]+\.[0-9]+\.[0-9]+)", releases["content"])
assert entry, "current-release sentence not found in fixture content"
print(json.dumps({"expected": entry.group(1)}))
