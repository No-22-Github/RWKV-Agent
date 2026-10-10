# DISTILL-CANARY-e0b94c73 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "press/cure-settings.csv"
text = case["files"][path]
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
values = sorted(set(re.findall(r"(\d+) percent", pages)))
if len(values) != 1:
    raise SystemExit("the lamp maker's pages do not agree on the lamp power")
filled = []
for line in text.split("\n"):
    if line.startswith("lamp_power_percent,"):
        line = "lamp_power_percent," + values[0]
    filled.append(line)
print(json.dumps({"files": {path: "\n".join(filled).rstrip("\n")}}))
