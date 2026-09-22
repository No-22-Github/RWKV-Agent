# WORKBANK-CANARY-7c4e9b31 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

docs = next(e for e in case["web_fixture"] if "docs.cindermill.dev" in e.get("url", ""))
row = re.search(r"\|\s*cache_ttl_hours\s*\|\s*integer\s*\|\s*(\d+)\s*\|", docs["content"])
assert row, "cache_ttl_hours row not found in fixture content"
print(json.dumps({"expected": row.group(1)}))
