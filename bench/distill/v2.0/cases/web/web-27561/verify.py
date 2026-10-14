# DISTILL-CANARY-09b25f24 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.thornbecktools.example/fieldbook/releases" in e.get("url", ""))
versions = [line.split()[1] for line in page["content"].splitlines() if line.startswith("## ")]
latest = max(versions, key=lambda v: [int(part) for part in v.split(".")])
print(json.dumps({"expected_string": latest}))
