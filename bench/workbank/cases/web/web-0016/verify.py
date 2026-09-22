# WORKBANK-CANARY-5e93c0b7 : bank artifact, excluded from training corpora
import json
import re

with open("case.json", encoding="utf-8") as fh:
    case = json.load(fh)

releases = next(e for e in case["web_fixture"] if "thornfield.dev/releases" in e.get("url", ""))
tagged = re.findall(r"## ([0-9]+\.[0-9]+\.[0-9]+) \(([0-9]{4}-[0-9]{2}-[0-9]{2})\)", releases["content"])
assert tagged, "no release headings found in fixture content"
newest = max(tagged, key=lambda pair: tuple(int(part) for part in pair[0].split(".")))
print(json.dumps({"expected": newest[0]}))
