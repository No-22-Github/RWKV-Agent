# WORKBANK-CANARY-b6d29e05 : bank artifact, excluded from training corpora
"""Expected answer for doc-0006: 4.8.1, the newest shipped release in CHANGELOG.md.

The changelog heads with 5.0.0-rc.3, a preview build with the highest version
number and the latest date; only entries tagged "shipped" reach customers. The
title line is required, so deleting it is detected.
"""
import json
import re

case = json.load(open("case.json"))
doc = case["files"]["CHANGELOG.md"]

lines = doc.splitlines()
if not lines or not lines[0].startswith("# "):
    raise SystemExit("changelog title line missing")

entries = re.findall(
    r"^##\s+([0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.]+)?)\s+-\s+(\w+)\s+-\s+"
    r"([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$",
    doc, re.M)
shipped = [version for version, channel, _ in entries if channel == "shipped"]
if not shipped:
    raise SystemExit("no shipped release found in CHANGELOG.md")

newest = max(shipped, key=lambda version: tuple(int(part) for part in version.split(".")))
print(json.dumps({"expected": newest}))
