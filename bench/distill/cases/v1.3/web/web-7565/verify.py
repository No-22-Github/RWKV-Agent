# DISTILL-CANARY-c0f846d7 : distillation case
import json

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.songjianbiji.example/desktop/changelog" in e.get("url", ""))
versions = [line.split()[1] for line in page["content"].splitlines() if line.startswith("## ")]
latest = max(versions, key=lambda v: [int(part) for part in v.split(".")])
print(json.dumps({"expected_string": latest}))
