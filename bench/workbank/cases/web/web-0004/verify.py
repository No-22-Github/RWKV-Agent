# WORKBANK-CANARY-09d4f7b2 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

changelog = next(e for e in case["web_fixture"] if "ferrocache.io/changelog" in e.get("url", ""))
entry = re.search(r"default shard_count is now (\d+)", changelog["content"])
assert entry, "4.2.0 default-change entry not found in fixture content"
print(json.dumps({"expected": entry.group(1)}))
