# DISTILL-CANARY-8c25fa40 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "metering/reporting-setup.txt"
text = case["files"][path]
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
values = sorted(set(re.findall(r"(\d+) seconds", pages)))
if len(values) != 1:
    raise SystemExit("the maker's pages do not agree on the interval")
filled = []
for line in text.split("\n"):
    if line.startswith("reporting_interval_seconds="):
        line = "reporting_interval_seconds=" + values[0]
    filled.append(line)
print(json.dumps({"files": {path: "\n".join(filled).rstrip("\n")}}))
