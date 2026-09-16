import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

docs = next(e for e in case["web_fixture"] if "docs.oxcart.dev" in e.get("url", ""))
row = re.search(r"\|\s*batch_size\s*\|\s*integer\s*\|\s*(\d+)\s*\|", docs["content"])
assert row, "batch_size row not found in fixture content"
print(json.dumps({"expected": row.group(1)}))
