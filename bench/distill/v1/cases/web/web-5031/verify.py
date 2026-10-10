# DISTILL-CANARY-a06f2d74 : distillation case
"""Recompute the Sedgebrook v9 contact importer notice period from the notice page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
importer = int(re.search(r"v9 contact importer keeps accepting uploads for (\d+) days", pages).group(1))
reports = int(re.search(r"v9 report endpoints keep answering for (\d+) days", pages).group(1))
if importer == reports:
    raise SystemExit("the importer and report notices must run on different clocks")
print(json.dumps({"expected_number": importer}))
