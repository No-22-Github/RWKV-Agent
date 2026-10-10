# DISTILL-CANARY-5899dd74 : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.mistlemoorsurvey.example/downloads" in e.get("url", ""))
match = re.search(r"Current stable build: (\d+\.\d+\.\d+)", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
