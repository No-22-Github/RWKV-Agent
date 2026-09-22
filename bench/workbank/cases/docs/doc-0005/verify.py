# WORKBANK-CANARY-3f8a1c47 : bank artifact, excluded from training corpora
"""Expected answer for doc-0005: 4.6.0, the newest release in CHANGELOG.md.

The changelog is the only place the released versions appear. It must open
with its title line; the release headings below it are parsed from the
fixture, so deleting the title line is detected.
"""
import json
import re

case = json.load(open("case.json"))
doc = case["files"]["CHANGELOG.md"]

lines = doc.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("changelog title line missing")

releases = re.findall(
    r"^##\s+([0-9]+\.[0-9]+\.[0-9]+)\s+-\s+([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$",
    doc, re.M)
if not releases:
    raise SystemExit("no release headings found in CHANGELOG.md")

newest = max(releases, key=lambda pair: tuple(int(part) for part in pair[0].split(".")))
print(json.dumps({"expected": newest[0]}))
