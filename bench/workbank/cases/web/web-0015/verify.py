# WORKBANK-CANARY-a1d74e28 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

guide = next(e for e in case["web_fixture"] if "docs.bellwether.dev/operating/sizing-and-limits" in e.get("url", ""))
entry = re.search(r"shipped default for max_concurrent_evaluations is (\d+) per node", guide["content"])
assert entry, "max_concurrent_evaluations default sentence not found in fixture content"
print(json.dumps({"expected": entry.group(1)}))
