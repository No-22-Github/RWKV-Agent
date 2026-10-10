# DISTILL-CANARY-2ebeabb5 : distillation case
import json
import re

case = json.load(open("case.json"))
log = [w for w in case["web_fixture"] if w["url"] == "https://larkspur.dev/changelog"][0]["content"]
print(json.dumps({"expected_number": int(re.search(r"lowered from \d+ s to (\d+) s", log).group(1))}))
