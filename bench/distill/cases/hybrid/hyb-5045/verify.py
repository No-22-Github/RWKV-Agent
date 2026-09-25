# DISTILL-CANARY-74c3e810 : distillation case
import json
import re

case = json.load(open("case.json"))
path = "kiln/firing-profile.csv"
text = case["files"][path]
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
body = re.search(r"clay_body,([a-z]+-[a-z]+)", text).group(1)
if not body.startswith("vennmoor-"):
    raise SystemExit("the profile must name one of the supplier's clay bodies")
shade = body.split("-", 1)[1]
soaks = dict(re.findall(r"Vennmoor ([a-z]+) stoneware is soaked for (\d+) minutes", pages))
if len(soaks) != 2:
    raise SystemExit("the supplier's notes do not give one soak per clay body")
soak = soaks[shade]
filled = []
for line in text.split("\n"):
    if line.startswith("soak_minutes,"):
        line = "soak_minutes," + soak
    filled.append(line)
print(json.dumps({"files": {path: "\n".join(filled).rstrip("\n")}}))
